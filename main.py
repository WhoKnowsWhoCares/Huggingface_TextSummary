import os
import asyncio
import random
import gradio as gr

from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated
from loguru import logger
from models.model import Summarizer, TextRequest, Result, DEFAULT_TEXT, SUMMARY_MODEL
from models.forms import VerificationForm
from models.exceptions import MyHTTPException, my_http_exception_handler
from models.security import AuthUsers, check_api_credentials
from dotenv import load_dotenv

load_dotenv()
SITE_KEY = os.getenv("SITE_KEY")

app = FastAPI()
users = AuthUsers()
pipe = Summarizer()

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

@app.on_event("startup")
async def set_event_loop():
    event_loop = asyncio.get_event_loop()
    pipe.set_loop(event_loop)
    
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
        context={"captcha_id": captcha_id, "site_key": SITE_KEY},
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


@app.get("/")
async def get_main_page():
    return RedirectResponse("/index", status_code=302)


@app.post("/get_summary_api", response_model=Result)
async def summ_api(
    request: TextRequest,
    username: Annotated[str, Depends(check_api_credentials)],
):
    results = pipe.summarize(request.text)
    logger.info(f"API response: {results}")
    return results


def get_summary(text: TextRequest, request: gr.Request):
    try:
        token = request.cookies["Authorization"]
        if users.verify_user(token):
            users.add_user_session(token)
            return pipe.get_summary(text)
    except KeyError:
        logger.error("User not verified")
    except Exception as e:
        logger.error(e)
    return "Sorry. You are not verified."


with gr.Blocks(css="/static/css/style.css") as demo:
    with gr.Column(scale=2, min_width=600):
        sum_description = gr.Markdown(value=f"Model for Summary: {SUMMARY_MODEL}")
        verify_href = gr.Markdown(
            value="Available only for verified users.[Click here for verification.](/verify_page)"
        )
        inputs = gr.Textbox(
            label="Input",
            lines=5,
            value=DEFAULT_TEXT,
            placeholder=DEFAULT_TEXT,
        )
        outputs = gr.Textbox(
            label="Output",
            lines=5,
            placeholder="Summary and Sentiment would be here...",
        )
        inbtn = gr.Button("Proceed")

    inbtn = inbtn.click(
        get_summary,
        [inputs],
        [outputs],
    )

# mounting at the root path
app = gr.mount_gradio_app(app, demo, path="/index")
