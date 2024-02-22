from sqlalchemy import create_engine, Column, BigInteger, String, Integer, Boolean, DateTime, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from api.models.unimed_model import DentistaModel
import os

load_dotenv()

DATABASE_URL = os.getenv("URI_MYSQL")
Base = declarative_base()

class DentistaOrm(Base):
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
    especialista = Column(Integer, default=False)
    tipo_pessoa = Column(String(2), default=None)
    relacao_operadora = Column(String(8), default=None)
    vinculacao_codigo = Column(String(16), default=None)
    vinculacao_nome = Column(String(220), default=None)
    vinculacao_razao_social = Column(String(220), default=None)
    vinculacao_cnpj = Column(String(220), default=None)
    logradouro = Column(String(220), default=None)
    bairro = Column(String(64), default=None)
    cidade = Column(String(64), default=None)
    uf = Column(String(2), default=None)
    latitude = Column(String(32), nullable=False)
    longitude = Column(String(32), nullable=False)
    areas_atuacao = Column(String(220), default=None)
    telefone = Column(String(220), nullable=False)
    email = Column(String(100), default=None)
    data_atualizacao = Column(DateTime(timezone=True), default=None)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=None)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'cro', 'cro_uf'),
    )

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autoflush=True, bind=engine)

class DentistaRepository:
    def insert_dentista(self, item: DentistaModel):

        dentista_orm = DentistaOrm(**item.model_dump())

        db = SessionLocal()
        try:
            db.add(dentista_orm)
            db.commit()
            db.refresh(dentista_orm)
            return dentista_orm
        finally:
            db.close()

    def update_dentista(self, id, item):
        db = SessionLocal()
        try:
            dentista_orm = db.query(DentistaOrm).filter(DentistaOrm.id == id).first()
            if dentista_orm:
                for key, value in item.dict(exclude_unset=True).items():
                    setattr(dentista_orm, key, value)
                db.commit()
                db.refresh(dentista_orm)

            return dentista_orm
        finally:
            db.close()

    def find_dentista(self, cro, cro_uf):
        db = SessionLocal()
        try:
            return db.query(DentistaOrm).filter(
                DentistaOrm.cro == cro,
                DentistaOrm.cro_uf == cro_uf
            ).first()
        finally:
            db.close()

    def find_dentistas(self):
        db = SessionLocal()
        try:
            return db.query(DentistaOrm).all()
        finally:
            db.close()
