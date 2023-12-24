import re

import gradio as gr
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from loguru import logger

# from pydantic import BaseModel

# RU_SUMMARY_MODEL = "IlyaGusev/rubart-large-sum"
# RU_SUMMARY_MODEL = "IlyaGusev/mbart_ru_sum_gazeta"
RU_SUMMARY_MODEL = "csebuetnlp/mT5_multilingual_XLSum"
# RU_SENTIMENT_MODEL = "IlyaGusev/rubart-large-sentiment"
RU_SENTIMENT_MODEL = "blanchefort/rubert-base-cased-sentiment"

EN_SUMMARY_MODEL = "csebuetnlp/mT5_multilingual_XLSum"
EN_SENTIMENT_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"


DEFAULT_EN_TEXT ="""Flags on official buildings are being flown at half-mast and a minute's silence will be observed at midday.
Fourteen people were shot dead at the Faculty of Arts building of Charles University in the capital by a student who then killed himself.
Police are working to uncover the motive behind the attack.
It is one of the deadliest assaults by a lone gunman in Europe this century.
Those killed in Thursday's attack included Lenka Hlavkova, head of the Institute of Musicology at the university.
Other victims were named as translator and Finnish literature expert Jan Dlask and student Lucie Spindlerova.
The shooting began at around 15:00 local time (14:00 GMT) at the Faculty of Arts building off Jan Palach Square in the centre of the Czech capital.
The gunman opened fire in the corridors and classrooms of the building, before shooting himself as security forces closed in on him, police say.
US tourist Hannah Mallicoat told the BBC that she and her family had been on Jan Palach Square during the attack.
"A crowd of people were crossing the street when the first shot hit. I thought it was something like a firecracker or a car backfire until I heard the second shot and people started running," she said.
"I saw a bullet hit the ground on the other side of the square about 30ft [9m] away before ducking into a store. The whole area was blocked off and dozens of police cars and ambulances were going towards the university."
In a statement, Czech Prime Minister Petr Fiala said the country had been shocked by this "horrendous act".
"It is hard to find the words to express condemnation on the one hand and, on the other, the pain and sorrow that our entire society is feeling in these days before Christmas."
The gunman is thought to have killed his father at a separate location. He is also suspected in the killing of a young man and his two-month-old daughter who were found dead in a forest on the outskirts of Prague on 15 December.
"""

DEFAULT_RU_TEXT = """В результате взрыва на заправке, который произошел накануне вечером, 
пострадали 56 человек, 13 из них — дети, сообщил минздрав Дагестана. 
Погибли 12 человек, в том числе двое несовершеннолетних. На место происшествия 
приехала глава минздрава республики Татьяна Беляева, она держит под личным контролем 
оказание помощи пострадавшим. В Махачкалу вылетел первый заместитель министра здравоохранения России Виктор Фисенко.
Врачам и пострадавшим помогают волонтеры Всероссийского студенческого корпуса спасателей 
и сотрудники некоммерческой организации «Добровольцы Дагестана», сообщило министерство молодежи Дагестана. 
Жители республики массово пришли сдавать кровь, заявил региональный минздрав. 
«Просим отложить визит на станцию переливания на завтра. Запасы крови есть, 
доноров для их пополнения на данный час тоже уже немало», — написало ведомство.
"""

class Summarizer():
    ru_summary_pipe: pipeline
    ru_sentiment_pipe: pipeline
    en_summary_pipe: pipeline
    en_sentiment_pipe: pipeline
    # sum_model_name = "csebuetnlp/mT5_multilingual_XLSum"
    # sum_tokenizer = AutoTokenizer.from_pretrained(sum_model_name)
    # sum_model = AutoModelForSeq2SeqLM.from_pretrained(sum_model_name)
    
    def __init__(self) -> None:
        sum_pipe = pipeline("summarization", model=RU_SUMMARY_MODEL, max_length=100, truncation=True)
        self.ru_summary_pipe = sum_pipe
        self.ru_sentiment_pipe = pipeline("sentiment-analysis", model=RU_SENTIMENT_MODEL)
        self.en_summary_pipe = sum_pipe
        self.en_sentiment_pipe = pipeline("sentiment-analysis", model=EN_SENTIMENT_MODEL)
        
        
    def mT5_summarize(self, text: str) -> str:

        WHITESPACE_HANDLER = lambda k: re.sub('\s+', ' ', re.sub('\n+', ' ', k.strip()))

        input_ids = self.sum_tokenizer(
            [WHITESPACE_HANDLER(text)],
            return_tensors="pt",
            padding="max_length",
            truncation=True,
            max_length=512
        )["input_ids"]

        output_ids = self.sum_model.generate(
            input_ids=input_ids,
            max_length=84,
            no_repeat_ngram_size=2,
            num_beams=4
        )[0]

        summary = self.sum_tokenizer.decode(
            output_ids,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False
        )

        return summary

    def get_pipe(self, lang: str):
        logger.info(f'Pipe language: {lang}')
        summary = {'en': self.en_summary_pipe,
                   'ru': self.ru_summary_pipe,}
        sentiment = {'en': self.en_sentiment_pipe,
                   'ru': self.ru_sentiment_pipe,}
        return summary[lang], sentiment[lang]
        
    def summarize(self, text: str, lang: str = 'en') -> str:
        result = {}
        sum_pipe, sent_pipe = self.get_pipe(lang)
        
        response_summary = sum_pipe(text)
        logger.info(response_summary)
        result["summary"] = response_summary[0]["summary_text"]
        
        response_sentiment = sent_pipe(text)
        logger.info(response_sentiment)
        result["sentiment_label"] = response_sentiment[0]["label"]
        result["sentiment_score"] = response_sentiment[0]["score"]
        
        return f"Summary:  {result['summary']}\n Sentiment:  {result['sentiment_label']} ({result['sentiment_score']:.3f})"    


if __name__ == "__main__":
    pipe = Summarizer()

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
            pipe.summarize,
            [en_inputs, en_lang],
            [en_outputs],
        )
        ru_inbtn.click(
            pipe.summarize,
            [ru_inputs, ru_lang],
            [ru_outputs],
        )
    demo.launch(show_api=False)   