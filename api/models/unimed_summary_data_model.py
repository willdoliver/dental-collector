from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class SummaryDataModel(BaseModel):
    id: Optional[int] = None
    url: str
    plano: int
    latitude: str
    longitude: str
    numero_pagina: int
    created_at: datetime = datetime.now()
    updated_at: datetime = None

    class Config:
        str_strip_whitespace = True
        populate_by_name = True
