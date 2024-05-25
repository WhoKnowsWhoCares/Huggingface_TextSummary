import os
from fastapi import Request
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"


class VerificationForm:
    request: Request

    def __init__(self, request: Request):
        self.request = request

    async def load_data(self):
        data = await self.request.form()
        captcha = data.get("captcha")
        captcha_id = data.get("captcha_id")
        g_recaptcha_response = data.get("g-recaptcha-response")
        logger.info(f"captcha_id: {captcha_id}")
        return captcha, captcha_id, g_recaptcha_response

    async def is_valid(self):
        captcha, captcha_id, g_recaptcha_response = await self.load_data()
        if (
            not captcha
            or not g_recaptcha_response
            or captcha.strip().lower() != os.getenv(f"CAPTCHA{captcha_id}")
        ):
            return False
        return True
