import sys
import traceback
from werkzeug.exceptions import HTTPException
from marshmallow import ValidationError
from src.core.responses import APIResponse
from src.core.logger import logger

class ApiError:
	@staticmethod
	def error_handler_resources(func):
		def wrapper(*args, **kwargs):
			try:
				return func(*args, **kwargs)
			except HTTPException as e:
				return APIResponse.error(message=e.description, status_code=e.code)
			except ValidationError as e:
				return APIResponse.error(data=e.messages, status_code=400)
			except Exception as e:
				exc_type, exc_value, exc_traceback = sys.exc_info()
				tb_frame = traceback.extract_tb(exc_traceback)[-1]
				file_path = tb_frame.filename 
				line_number = tb_frame.lineno 
				logger.error(
					extra={"file_path": file_path, "line_number": line_number},
					msg=f"{e}",
				)
				return APIResponse.error(message=str(e), status_code=500)
		return wrapper