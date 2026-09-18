import sys
import traceback

from werkzeug.exceptions import HTTPException
from marshmallow import ValidationError

from ..core.responses import APIResponse
from ..core.logger import logger


def normalize_error(e):
    if isinstance(e, HTTPException):
        return APIResponse.error(message=e.description, status_code=e.code)

    if isinstance(e, ValidationError):
        return APIResponse.error(data=e.messages, status_code=400)

    exc_type, exc_value, exc_traceback = sys.exc_info()
    tb_frame = traceback.extract_tb(exc_traceback)[-1]
    logger.error(
        extra={
            "file_path": tb_frame.filename,
            "line_number": tb_frame.lineno,
        },
        msg=f"{e}",
    )
    return APIResponse.error(message=str(e), status_code=500)


def wrap_resource(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except (HTTPException, ValidationError, Exception) as e:
            return normalize_error(e)

    return wrapper
