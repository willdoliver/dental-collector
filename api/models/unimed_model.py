import uuid
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class Dentista(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    nome: str
    cro: str = Field(max_length=6, pattern=r'^\d*$')
    uf_cro: str = Field(max_length=2, alias='ufCro')
    codigo_prestador: str | None = Field(alias="codigoPrestador")
    cpf_cnpj: str | None = Field(pattern=r'^\d*$', alias="cpfCnpj")
    razao_social: str | None = Field(alias="razaoSocial")
    rede: str | None
    tipo_estabelecimento: str | None = Field(alias="tipoEstabelecimento")
    website: str | None
    especialista: bool | None
    tipo_pessoa: str | None = Field(max_length=2, alias="tipoPessoa")
    relacao_peradora: str | None = Field(alias="relacaoOperadora")
    vinculacao_codigo: str | None = Field(alias="vinculacaoCodigo")
    vinculacao_nome: str | None = Field(alias="vinculacaoNome")
    vinculacao_razao_social: str | None = Field(alias="vinculacaoRazaoSocial")
    vinculacao_cnpj: str | None = Field(alias="vinculacaoCnpj")
    locaisAtendimento: list = Field(alias="locais_atendimento")
    data_atualizacao: str | None = Field(alias="dataAtualizacao")

    class Config:
        str_strip_whitespace = True
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "nome": "João Maria da Silva",
                "cro": "12345",
                "ufCro": "PR"
            }
        }

class DentistaUpdate(BaseModel):
    nome: Optional[str]
    cro: Optional[str]
    uf_cro: Optional[str]
    codigo_prestador: Optional[str]
    cpf_cnpj: Optional[str]
    razao_social: Optional[str]
    rede: Optional[str]
    tipo_estabelecimento: Optional[str]
    website: Optional[str]
    especialista: Optional[str]
    tipo_pessoa: Optional[str]
    relacao_peradora: Optional[str]
    vinculacao_codigo: Optional[str]
    vinculacao_nome: Optional[str]
    vinculacao_razao_social: Optional[str]
    vinculacao_cnpj: Optional[str]
    locaisAtendimento: Optional[dict]
    data_atualizacao: Optional[dict]

    class Config:
        str_strip_whitespace = True
        json_schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "nome": "João Maria da Silva",
                "cro": "12345",
                "ufCro": "PR"
            }
        }

class URLCrawled(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    url: str
    plano: int
    latitude: str
    longitude: str
    pagina: int
    created_at: datetime = datetime.now()

    class Config:
        str_strip_whitespace = True
        populate_by_name = True
