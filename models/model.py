import asyncio
import gc
from pydantic import BaseModel
from transformers import pipeline
from loguru import logger

SUMMARY_MODEL = "csebuetnlp/mT5_multilingual_XLSum"
MODEL_DIRECOTRY = "./data"
TIME_TO_RELEASE = 10 * 60

DEFAULT_TEXT = """Flags on official buildings are being flown at half-mast and a minute's silence will be observed at midday.
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


class TextRequest(BaseModel):
    text: str


class Result(BaseModel):
    summary: str

    def to_str(self):
        return f"Summary:  {self.summary}"


class Timer:
    def __init__(self, timeout, callback, event_loop):
        self.task = event_loop.create_task(self.job(timeout, callback))

    async def job(self, timeout, callback):
        await asyncio.sleep(timeout)
        await callback()

    def cancel(self):
        self.task.cancel()


class Summarizer(object):
    _release_timer: Timer
    _summary_pipe: pipeline

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(Summarizer, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self._release_timer = None
        self._summary_pipe = None
        # summary_pipe = pipeline(
        #     "summarization", model=SUMMARY_MODEL, max_length=512, truncation=True
        # )
        # summary_pipe.save_pretrained(MODEL_DIRECOTRY)
        # del summary_pipe
        gc.collect()

    def set_loop(self, loop):
        self.loop = loop

    def release_resources(self):
        del self._summary_pipe
        self._summary_pipe = None
        gc.collect()

    async def timeout_callback(self):
        await asyncio.sleep(0.1)
        self.release_resources()
        logger.info("Model released")

    def summarize(self, req: TextRequest) -> Result:
        if not self._summary_pipe:
            self._summary_pipe = pipeline("summarization", model=MODEL_DIRECOTRY)
        try:
            if self._release_timer:
                logger.info("Cancelling release timer")
                self._release_timer.cancel()
            result = self._summary_pipe(req)[0]["summary_text"]
            logger.info("Starting release timer")
            self._release_timer = Timer(
                TIME_TO_RELEASE, self.timeout_callback, self.loop
            )
            return Result(summary=result)
        except Exception as e:
            logger.error(e)
            return Result(summary="Sorry, something went wrong")

    def get_summary(self, req: TextRequest) -> str:
        return self.summarize(req).to_str()
