from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def error_response(code: str, message: str, status_code: int) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": message,
            },
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        _request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        if exc.status_code == status.HTTP_404_NOT_FOUND:
            return error_response("RESOURCE_NOT_FOUND", "요청한 경로를 찾을 수 없습니다.", 404)

        return error_response("HTTP_ERROR", "요청 처리 중 오류가 발생했습니다.", exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request, _exc: RequestValidationError
    ) -> JSONResponse:
        return error_response("VALIDATION_ERROR", "요청 값이 올바르지 않습니다.", 422)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_request: Request, _exc: Exception) -> JSONResponse:
        return error_response("INTERNAL_SERVER_ERROR", "서버 오류가 발생했습니다.", 500)
