import os
import gradio as gr
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from app import Summarizer, TextRequest, Result
from app import (
    EN_SENTIMENT_MODEL,
    EN_SUMMARY_MODEL,
    RU_SENTIMENT_MODEL,
    RU_SUMMARY_MODEL,
)
from app import DEFAULT_EN_TEXT, DEFAULT_RU_TEXT

load_dotenv()

SITE_KEY = os.getenv("SITE_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"

# create FastAPI app
app = FastAPI()
pipe = Summarizer()

# create a static directory to store the static files
static_dir = Path("./static")
static_dir.mkdir(parents=True, exist_ok=True)

# mount FastAPI StaticFiles server
app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/verify_page", response_class=HTMLResponse)
async def verify_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="verification.html", context={"site_key": SITE_KEY}
    )


@app.get("/bad_request", response_class=HTMLResponse)
async def bad_request(request: Request):
    return templates.TemplateResponse("bad_request.html", {"request": request})


@app.post("/verify")
async def verify(request: Request):
    # verify_response = requests.post(
    #     url=VERIFY_URL,
    #     data={
    #         "secret": SECRET_KEY,
    #         "response": request.form["g-recaptcha-response"],
    #     },
    # )
    # print(verify_response.json())
    return templates.TemplateResponse("bad_request.html", {"request": request})


@app.post("/summ_ru", response_model=Result)
async def ru_summ_api(request: TextRequest):
    results = pipe.summarize(request.text, lang="ru")
    return results


@app.post("/summ_en", response_model=Result)
async def en_summ_api(request: TextRequest):
    results = pipe.summarize(request.text, lang="en")
    return results


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
app = gr.mount_gradio_app(app, demo, path="/")
