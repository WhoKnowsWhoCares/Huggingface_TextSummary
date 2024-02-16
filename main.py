import random
import gradio as gr

# from fastapi.security import APIKeyHeader
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated
from loguru import logger
from app import Summarizer, TextRequest, Result
from app import (
    DEFAULT_EN_TEXT,
    EN_SENTIMENT_MODEL,
    EN_SUMMARY_MODEL,
)

from models.forms import VerificationForm
from models.exceptions import MyHTTPException, my_http_exception_handler
from models.security import AuthUsers, check_api_credentials


app = FastAPI()
pipe = Summarizer()
users = AuthUsers()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# auth_header = APIKeyHeader(name="Authorization", auto_error=True)
# router = APIRouter(
#     prefix="/v1",
#     tags=["API v1"],
#     dependencies=[Security(auth_header)],
# )
# app.include_router(router)

app.add_exception_handler(MyHTTPException, my_http_exception_handler)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    response = await call_next(request)
    token = request.cookies.get("Authorization")
    dest = request.url.path.split("/")[-1]
    resp_headers = dict(response.headers)
    cont_type = resp_headers.get("content-type")
    if (
        not cont_type
        or "text/html" not in cont_type
        or dest
        in [
            "docs",
            "verify_page",
            "verify",
        ]
    ):
        return response
    if not token or token == "":
        return RedirectResponse("/verify_page", status_code=307)
    return response


@app.get("/verify_page", response_class=HTMLResponse)
async def verify_page(request: Request):
    captcha_id = random.randint(1, 5)
    return templates.TemplateResponse(
        request=request,
        name="verification.html",
        context={"captcha_id": captcha_id},
    )


@app.post("/verify")
async def verify(request: Request, token: str = Depends(users.get_cookie_data)):
    form = VerificationForm(request)
    await form.load_data()
    if await form.is_valid():
        logger.info("Form is valid")
        response = RedirectResponse("/index", status_code=302)
        response.set_cookie(key="Authorization", value=token)
        return response
    logger.info("Validation error")
    return await verify_page(request)


@app.post("/get_summary_api", response_model=Result)
async def summ_api(
    request: TextRequest,
    lang: str,
    username: Annotated[str, Depends(check_api_credentials)],
):
    results = pipe.summarize(request.text, lang=lang)
    logger.info(f"API response: {results}")
    return results


@app.get("/")
async def get_main_page():
    return RedirectResponse("/index", status_code=302)


def get_summary(text: TextRequest, lang: str, request: gr.Request):
    token = request.cookies["Authorization"]
    if users.verify_user(token):
        users.add_user_session(token)
        return pipe.get_summary(text, lang)
    logger.info("User not verified")
    return "Sorry. You are not verified."


with gr.Blocks(css="/static/css/style.css") as demo:
    with gr.Column(scale=2, min_width=600):
        en_sum_description = gr.Markdown(value=f"Model for Summary: {EN_SUMMARY_MODEL}")
        en_sent_description = gr.Markdown(
            value=f"Model for Sentiment: {EN_SENTIMENT_MODEL}"
        )
        verify_href = gr.Markdown(
            value="Available only for verified users.[Click here for verification.](/verify_page)"
        )
        en_inputs = gr.Textbox(
            label="Input",
            lines=5,
            value=DEFAULT_EN_TEXT,
            placeholder=DEFAULT_EN_TEXT,
        )
        # en_lang = gr.Textbox(value="en", visible=False)
        en_lang = gr.Radio(["en", "ru"], value="en", label="Language")
        en_outputs = gr.Textbox(
            label="Output",
            lines=5,
            placeholder="Summary and Sentiment would be here...",
        )
        en_inbtn = gr.Button("Proceed")

    en_inbtn = en_inbtn.click(
        get_summary,
        [en_inputs, en_lang],
        [en_outputs],
    )

# mounting at the root path
app = gr.mount_gradio_app(app, demo, path="/index")
