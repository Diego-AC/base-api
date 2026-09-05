class APIResponse:
    @staticmethod
    def success(
        message: str = "Ok",
        status: int = 1,
        data: dict = {},
        status_code: int = 200
    ):
        """Creates a base response dictionary."""
        return {
            "message": message,
            "status": status,
            "data": data
        }, status_code
    
    @staticmethod
    def error(
        message: str = "Error",
        status: int = 0,
        data: dict = {},
        status_code: int = 500
    ):
        """Creates a base response dictionary."""
        return {
            "message": message,
            "status": status,
            "data": data
        }, status_code
