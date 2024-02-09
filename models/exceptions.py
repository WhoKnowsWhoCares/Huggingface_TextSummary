from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="templates")


class MyHTTPException(HTTPException):
    pass


def my_http_exception_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        "errors/error.html",
        {"request": request, "message": f"{exc.status_code}. {exc.detail}."},
        status_code=exc.status_code,
    )
