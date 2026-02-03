from typing import Optional

from pydantic import BaseModel, Field


class QueryParams(BaseModel):
    limit: Optional[int] = Field(100, ge=1, le=1000)
    offset: Optional[int] = Field(0, ge=0)
