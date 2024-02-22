from sqlalchemy import create_engine, Column, BigInteger, String, Integer, Boolean, DateTime, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from api.models.metlife_model import DentistaModel
import os

load_dotenv()

DATABASE_URL = os.getenv("URI_MYSQL")
Base = declarative_base()

class DentistaOrm(Base):
    __tablename__ = os.getenv("METLIFE_TABLE_DENTISTAS")

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nome = Column(String(220), nullable=False)
    cro = Column(String(16), primary_key=True, nullable=False)
    uf = Column(String(2), primary_key=True, nullable=False)
    cpf_cnpj = Column(String(220), default=None)
    tipo_estabelecimento = Column(String(220), default=None)
    logradouro = Column(String(220), default=None)
    cidade = Column(String(64), default=None)
    especialidade = Column(String(220), default=None)
    telefone = Column(String(220), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=None)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'cro', 'uf'),
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

    def update_dentista(self, id, especialidade, item):
        db = SessionLocal()
        try:
            dentista_orm = db.query(DentistaOrm).filter(
                DentistaOrm.id == id,
                DentistaOrm.especialidade == especialidade
            ).first()

            if dentista_orm:
                for key, value in item.dict(exclude_unset=True).items():
                    setattr(dentista_orm, key, value)
                db.commit()
                db.refresh(dentista_orm)

            return dentista_orm
        finally:
            db.close()

    def find_dentista(self, cro, uf, especialidade):
        db = SessionLocal()
        try:
            return db.query(DentistaOrm).filter(
                DentistaOrm.cro == cro,
                DentistaOrm.uf == uf,
                DentistaOrm.especialidade == especialidade
            ).first()
        finally:
            db.close()

    def find_dentistas(self):
        db = SessionLocal()
        try:
            return db.query(DentistaOrm).all()
        finally:
            db.close()
