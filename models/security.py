import os
import secrets
from typing import Annotated
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import status, Depends, Cookie
from datetime import datetime, timedelta
from collections import defaultdict
from loguru import logger
from dotenv import load_dotenv

from models.exceptions import MyHTTPException

load_dotenv()

API_USER = os.getenv("API_USER")
API_PWD = os.getenv("API_PWD")
API_KEY = os.getenv("API_KEY")

security = HTTPBasic()


class AuthUsers:
    REQUESTS_LIMIT = 3  # 3 REQUESTS PER MINUTE
    AUTH_TIME = 10  # 10 MINUTES
    users: set
    users_auth: defaultdict(list)

    def __init__(self):
        self.users = set()
        self.users_auth = defaultdict(list)

    def generate_user_token(self) -> str:
        return secrets.token_hex(16)

    def verify_user(self, user_token: str) -> bool:
        logger.info(f"Check user token: {user_token}")
        if user_token in self.users:
            print(self.users_auth[user_token])
            if len(self.users_auth[user_token]) < self.REQUESTS_LIMIT:
                return True
            elif datetime.now() - self.users_auth[user_token][
                -self.REQUESTS_LIMIT
            ] >= timedelta(minutes=self.AUTH_TIME):
                return True
            else:
                raise MyHTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests. Try again later.",
                )
        logger.info(f"User {user_token} not found")
        raise MyHTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized user",
        )

    def add_user_session(self, user_token: str):
        if user_token in self.users:
            self.users_auth[user_token].append(datetime.now())
        else:
            self.users.add(user_token)
            self.users_auth.setdefault(user_token, []).append(datetime.now())
            print(self.users_auth[user_token])
            while len(self.users_auth[user_token]) > self.REQUESTS_LIMIT:
                self.users_auth[user_token].pop(0)
        logger.info(f"User's {user_token} session added")

    def get_cookie_data(
        self, user_token: str = Cookie(default=None, alias="Authorization")
    ) -> list:
        if not user_token or user_token not in self.users:
            logger.info("Unauthorized user")
            return False
        logger.info(f"Verified user with token: {user_token}")
        return True


credentials_exception = MyHTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Login or password is incorrect",
    headers={"WWW-Authenticate": "Basic"},
)


def check_api_credentials(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = bytes(API_USER, "utf-8")
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = bytes(API_PWD, "utf-8")
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise credentials_exception
    return credentials.username
