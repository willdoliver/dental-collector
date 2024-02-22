from typing import Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime

class SummaryDataModel(BaseModel):
    uf: str = Field(max_length=2)
    cidade: str = None
    count_dentistas: Union[int, int] = Field(default=0)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        str_strip_whitespace = True
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "uf": "PR",
                "cidade": "Curitiba",
                "dentistas": "48",
            }
        }