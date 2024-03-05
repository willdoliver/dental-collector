from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class DentistaModel(BaseModel):
    id: Optional[int] = None
    nome: str
    cro: str = Field(max_length=16)
    uf: str = Field(max_length=2)
    cpf_cnpj: str | None = Field(pattern=r'^\d*$', alias="cpfCnpj")
    razao_social: str | None = Field(alias="razaoSocial")
    tipo_estabelecimento: str | None = Field(alias="tipoEstabelecimento")
    logradouro: str = None
    bairro: str = None
    cidade: str = None
    latitude: str = None
    longitude: str = None
    areas_atuacao: str = None
    telefone: str = None
    email: str = None
    data_atualizacao: Optional[datetime] | None = Field(alias="dataAtualizacao")
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
                "uf": "PR"
            }
        }
