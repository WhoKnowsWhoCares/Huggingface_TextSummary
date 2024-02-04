import os
import gradio as gr
import random
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import HTTPException
from loguru import logger
from dotenv import load_dotenv

from app import Summarizer, TextRequest, Result
from app import (
    EN_SENTIMENT_MODEL,
    EN_SUMMARY_MODEL,
    RU_SENTIMENT_MODEL,
    RU_SUMMARY_MODEL,
)
from app import DEFAULT_EN_TEXT, DEFAULT_RU_TEXT
from models.forms import VerificationForm

load_dotenv()

SITE_KEY = os.getenv("SITE_KEY")

app = FastAPI()
pipe = Summarizer()

# mount FastAPI StaticFiles server
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def index(request: Request):
    return RedirectResponse("/index/", status_code=302)


@app.get("/verify_page", response_class=HTMLResponse)
async def verify_page(request: Request):
    captcha_id = random.randint(1, 5)
    return templates.TemplateResponse(
        request=request,
        name="verification.html",
        context={"site_key": SITE_KEY, "captcha_id": captcha_id},
    )


@app.post("/verify")
async def verify(request: Request):
    form = VerificationForm(request)
    await form.load_data()
    if await form.is_valid():
        logger.info("Form is valid")
        return RedirectResponse("/index/", status_code=302)
    return await verify_page(request)


@app.post("/summ_ru", response_model=Result)
async def ru_summ_api(request: TextRequest):
    results = pipe.summarize(request.text, lang="ru")
    logger.info(results)
    return results


@app.post("/summ_en", response_model=Result)
async def en_summ_api(request: TextRequest):
    results = pipe.summarize(request.text, lang="en")
    logger.info(results)
    return results


@app.exception_handler(403)
async def unavailable_error(request: Request, exc: HTTPException):
    logger.warning("Error 403")
    return templates.TemplateResponse(
        "errors/error.html",
        {"request": request, "message": "403. Sorry, this page unavailable."},
        status_code=403,
    )


@app.exception_handler(404)
async def not_found_error(request: Request, exc: HTTPException):
    logger.warning("Error 404")
    return templates.TemplateResponse(
        "errors/error.html",
        {"request": request, "message": "404. Page Not Found."},
        status_code=404,
    )


@app.exception_handler(500)
async def internal_error(request: Request, exc: HTTPException):
    logger.warning("Error 500")
    return templates.TemplateResponse(
        "errors/error.html",
        {"request": request, "message": "500. Oops. Something has gone wrong."},
        status_code=500,
    )


with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column(scale=2, min_width=600):
            en_sum_description = gr.Markdown(
                value=f"Model for Summary: {EN_SUMMARY_MODEL}"
            )
            en_sent_description = gr.Markdown(
                value=f"Model for Sentiment: {EN_SENTIMENT_MODEL}"
            )
            en_inputs = gr.Textbox(
                label="en_input",
                lines=5,
                value=DEFAULT_EN_TEXT,
                placeholder=DEFAULT_EN_TEXT,
            )
            en_lang = gr.Textbox(value="en", visible=False)
            en_outputs = gr.Textbox(
                label="en_output",
                lines=5,
                placeholder="Summary and Sentiment would be here...",
            )
            en_inbtn = gr.Button("Proceed")
        with gr.Column(scale=2, min_width=600):
            ru_sum_description = gr.Markdown(
                value=f"Model for Summary: {RU_SUMMARY_MODEL}"
            )
            ru_sent_description = gr.Markdown(
                value=f"Model for Sentiment: {RU_SENTIMENT_MODEL}"
            )
            ru_inputs = gr.Textbox(
                label="ru_input",
                lines=5,
                value=DEFAULT_RU_TEXT,
                placeholder=DEFAULT_RU_TEXT,
            )
            ru_lang = gr.Textbox(value="ru", visible=False)
            ru_outputs = gr.Textbox(
                label="ru_output",
                lines=5,
                placeholder="Здесь будет обобщение и эмоциональный окрас текста...",
            )
            ru_inbtn = gr.Button("Запустить")

    en_inbtn.click(
        pipe.summ,
        [en_inputs, en_lang],
        [en_outputs],
    )
    ru_inbtn.click(
        pipe.summ,
        [ru_inputs, ru_lang],
        [ru_outputs],
    )

# mounting at the root path
app = gr.mount_gradio_app(app, demo, path="/index")
