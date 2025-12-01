from typing import TypeVar
from pydantic import BaseModel

ReqModel = TypeVar("ReqModel", bound=BaseModel)
RespModel = TypeVar("RespModel", bound=BaseModel)
