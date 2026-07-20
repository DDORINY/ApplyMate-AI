from typing import Generic, TypeVar

from pydantic import BaseModel

DataT = TypeVar("DataT")


class ApiResponse(BaseModel, Generic[DataT]):
    success: bool
    data: DataT
    message: str


class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: str | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail


class HealthData(BaseModel):
    status: str
    database: str
    redis: str
    required_settings: str = "UP"
