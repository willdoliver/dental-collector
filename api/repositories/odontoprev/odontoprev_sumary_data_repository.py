from sqlalchemy import create_engine, Column, BigInteger, String, Integer, Boolean, DateTime, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from api.models.odontoprev_summary_data_model import SummaryDataModel
from datetime import datetime, timedelta
import os

load_dotenv()

DATABASE_URL = os.getenv("URI_MYSQL")
Base = declarative_base()

class SummaryDataOrm(Base):
    __tablename__ = os.getenv("ODONTOPREV_TABLE_SUMARY_DATA")

    uf = Column(String(2), primary_key=True, nullable=False)
    cidade = Column(String(64), primary_key=True, default=None)
    count_dentistas = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=None)

    __table_args__ = (
        PrimaryKeyConstraint('uf', 'cidade'),
    )

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autoflush=True, bind=engine)

class SummaryDataRepository:
    def insert_data(self, item: SummaryDataModel):

        sumary_data_orm = SummaryDataOrm(**item.model_dump())

        db = SessionLocal()
        try:
            db.add(sumary_data_orm)
            db.commit()
            db.refresh(sumary_data_orm)
            return sumary_data_orm
        finally:
            db.close()

    def update_data(self, uf, city, item):
        db = SessionLocal()
        try:
            dentista_orm = db.query(SummaryDataOrm).filter(
                SummaryDataOrm.uf == uf,
                SummaryDataOrm.cidade == city
            ).first()

            if dentista_orm:
                for key, value in item.dict(exclude_unset=True).items():
                    setattr(dentista_orm, key, value)
                db.commit()
                db.refresh(dentista_orm)

            return dentista_orm
        finally:
            db.close()

    def find_data(self, uf, cidade):
        db = SessionLocal()
        try:
            five_days_ago = datetime.now() - timedelta(days=5)
            return db.query(SummaryDataOrm).filter(
                SummaryDataOrm.uf == uf,
                SummaryDataOrm.cidade == cidade,
                SummaryDataOrm.created_at < five_days_ago.strftime('%Y-%m-%d %H:%M:%S')
            ).first()
        finally:
            db.close()
