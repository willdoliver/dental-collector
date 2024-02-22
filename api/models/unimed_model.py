from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class DentistaModel(BaseModel):
    id: Optional[int] = None
    nome: str
    cro: str = Field(max_length=16)
    cro_uf: str = Field(max_length=2, alias='ufCro')
    codigo_prestador: str | None = Field(alias="codigoPrestador")
    cpf_cnpj: str | None = Field(pattern=r'^\d*$', alias="cpfCnpj")
    razao_social: str | None = Field(alias="razaoSocial")
    rede: str | None
    tipo_estabelecimento: str | None = Field(alias="tipoEstabelecimento")
    website: str | None
    especialista: int = None
    tipo_pessoa: str | None = Field(max_length=2, alias="tipoPessoa")
    relacao_operadora: str | None = Field(alias="relacaoOperadora")
    vinculacao_codigo: str | None = Field(alias="vinculacaoCodigo")
    vinculacao_nome: str | None = Field(alias="vinculacaoNome")
    vinculacao_razao_social: str | None = Field(alias="vinculacaoRazaoSocial")
    vinculacao_cnpj: str | None = Field(alias="vinculacaoCnpj")
    logradouro: str = None
    bairro: str = None
    cidade: str = None
    uf: str = None
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
                "cro_uf": "PR"
            }
        }

class URLCrawledModel(BaseModel):
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
