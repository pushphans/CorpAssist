from typing import Annotated

from pydantic import BaseModel, StringConstraints


class AiRequestSchema(BaseModel):
    message: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class AiResponseSchema(BaseModel):
    message: str
