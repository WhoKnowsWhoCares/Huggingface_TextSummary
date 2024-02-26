import os
from typing import Optional
from fastapi import Request
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"


class VerificationForm:
    request: Request
    captcha: Optional[str] = None

    def __init__(self, request: Request):
        self.request = request

    async def load_data(self):
        data = await self.request.form()
        self.captcha = data.get("captcha")
        self.captcha_id = data.get("captcha_id")
        logger.info(f"captcha: {self.captcha}")
        logger.info(f"captcha_id: {self.captcha_id}")
        # self.g_recaptcha_response = data.get("g-recaptcha-response")

    async def is_valid(self):
        if not self.captcha or self.captcha.strip().lower() != os.getenv(
            f"CAPTCHA{self.captcha_id}"
        ):
            return False
        return True
