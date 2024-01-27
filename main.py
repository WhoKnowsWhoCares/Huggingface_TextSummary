import gradio as gr
from fastapi import FastAPI
from typing import List
from app import Summarizer, Request, Result
from app import EN_SENTIMENT_MODEL, EN_SUMMARY_MODEL, RU_SENTIMENT_MODEL, RU_SUMMARY_MODEL
from app import DEFAULT_EN_TEXT, DEFAULT_RU_TEXT

app = FastAPI()
pipe = Summarizer()


@app.post("/summ_ru", response_model=Result)
async def ru_summ_api(request: Request):
    results = pipe.summarize(request.text)
    return results
    
    
if __name__ == "__main__":

    with gr.Blocks() as demo:
        with gr.Row():
            with gr.Column(scale=2, min_width=600):
                en_sum_description=gr.Markdown(value=f"Model for Summary: {EN_SUMMARY_MODEL}")
                en_sent_description=gr.Markdown(value=f"Model for Sentiment: {EN_SENTIMENT_MODEL}")
                en_inputs=gr.Textbox(label="en_input", lines=5, value=DEFAULT_EN_TEXT, placeholder=DEFAULT_EN_TEXT)
                en_lang=gr.Textbox(value='en',visible=False)
                en_outputs=gr.Textbox(label="en_output", lines=5, placeholder="Summary and Sentiment would be here...")
                en_inbtn = gr.Button("Proceed")
            with gr.Column(scale=2, min_width=600):
                ru_sum_description=gr.Markdown(value=f"Model for Summary: {RU_SUMMARY_MODEL}")
                ru_sent_description=gr.Markdown(value=f"Model for Sentiment: {RU_SENTIMENT_MODEL}")
                ru_inputs=gr.Textbox(label="ru_input", lines=5, value=DEFAULT_RU_TEXT, placeholder=DEFAULT_RU_TEXT)
                ru_lang=gr.Textbox(value='ru',visible=False)
                ru_outputs=gr.Textbox(label="ru_output", lines=5, placeholder="Здесь будет обобщение и эмоциональный окрас текста...")
                ru_inbtn = gr.Button("Запустить")
                
        en_inbtn.click(
            pipe.summarize.to_str(),
            [en_inputs, en_lang],
            [en_outputs],
        )
        ru_inbtn.click(
            pipe.summarize.to_str(),
            [ru_inputs, ru_lang],
            [ru_outputs],
        )
    demo.launch(show_api=False)   