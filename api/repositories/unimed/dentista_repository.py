from sqlalchemy import create_engine, Column, BigInteger, String, Integer, Boolean, DateTime, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("URL_MYSQL_UNIMED")

Base = declarative_base()

class Dentista(Base):
    __tablename__ = os.getenv("UNIMED_TABLE_DENTISTAS")

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nome = Column(String(220), nullable=False)
    cro = Column(String(16), primary_key=True, nullable=False)
    cro_uf = Column(String(2), primary_key=True, nullable=False)
    codigo_prestador = Column(String(16), default=None)
    cpf_cnpj = Column(String(220), default=None)
    razao_social = Column(String(220), default=None)
    rede = Column(String(100), default=None)
    tipo_estabelecimento = Column(String(220), default=None)
    website = Column(String(100), default=None)
    especialista = Column(Boolean, default=False)
    tipo_pessoa = Column(String(2), default=None)
    relacao_peradora = Column(String(8), default=None)
    vinculacao_codigo = Column(String(16), default=None)
    vinculacao_nome = Column(String(220), default=None)
    vinculacao_razao_social = Column(String(220), default=None)
    vinculacao_cnpj = Column(String(220), default=None)
    logradouro = Column(String(220), default=None)
    bairro = Column(String(64), default=None)
    cidade = Column(String(64), default=None)
    uf = Column(String(2), default=None)
    latitude = Column(String(16), nullable=False)
    longitude = Column(String(16), nullable=False)
    areasAtuacao = Column(String(220), nullable=False)
    telefone = Column(String(220), nullable=False)
    email = Column(String(100), default=None)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), default=None)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'cro', 'cro_uf'),
    )

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class DentistaRepository:
    def create_item(self, item):
        db = SessionLocal()
        try:
            db.add(item)
            db.commit()
            db.refresh(item)
            return item
        finally:
            db.close()

    def get_item(self, item_id):
        db = SessionLocal()
        try:
            return db.query(Dentista).filter(Dentista.id == item_id).first()
        finally:
            db.close()
