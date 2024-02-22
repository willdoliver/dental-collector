from typing import Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime

class DentistaModel(BaseModel):
    id: Optional[int] = None
    nome: str
    cro: str = Field(max_length=16)
    uf: str = Field(max_length=2)
    cpf_cnpj: str | None = Field(pattern=r'^\d*$')
    tipo_estabelecimento: str | None 
    logradouro: str = None
    cidade: str = None
    especialidade: str = None
    telefone: str = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        str_strip_whitespace = True
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": 123,
                "nome": "João Maria da Silva",
                "cro": "12345",
                "cro_uf": "PR"
            }
        }
