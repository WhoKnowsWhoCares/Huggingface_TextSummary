import gradio as gr
from transformers import pipeline
from loguru import logger
# from pydantic import BaseModel

# RU_SUMMARY_MODEL = "IlyaGusev/rubart-large-sum"
RU_SUMMARY_MODEL = "IlyaGusev/mbart_ru_sum_gazeta"
# RU_SENTIMENT_MODEL = "IlyaGusev/rubart-large-sentiment"
RU_SENTIMENT_MODEL = "seara/rubert-tiny2-russian-sentiment"
EN_SUMMARY_MODEL = "sshleifer/distilbart-cnn-12-6"
EN_SENTIMENT_MODEL = "ProsusAI/finbert"

class Summarizer():
    ru_summary_pipe: pipeline
    ru_sentiment_pipe: pipeline
    
    def __init__(self) -> None:
        self.ru_summary_pipe = pipeline("summarization", model=RU_SUMMARY_MODEL, max_length=100, truncation=True)
        self.ru_sentiment_pipe = pipeline("sentiment-analysis", model=RU_SENTIMENT_MODEL)
        
    def summarize(self, text: str) -> str:
        result = {}
        response_summary = self.ru_summary_pipe(text)
        logger.info(response_summary)
        result["summary"] = response_summary[0]["summary_text"]
        
        response_sentiment = self.ru_sentiment_pipe(text)
        logger.info(response_sentiment)
        result["sentiment"] = response_sentiment[0]["label"]
        
        return f"Summary: {result['summary']}\n Sentiment:{result['sentiment']}"

pipe = Summarizer()
    
demo = gr.Interface(
    fn=pipe.summarize, 
    inputs=gr.Textbox(lines=5, placeholder="Write your text here..."), 
    outputs=gr.Textbox(lines=5, placeholder="Summary and Sentiment would be here..."), 
)
    
if __name__ == "__main__":
    demo.launch(show_api=False)   