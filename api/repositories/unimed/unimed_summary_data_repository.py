from sqlalchemy import create_engine, Column, BigInteger, String, Integer, Boolean, DateTime, PrimaryKeyConstraint, or_, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os

load_dotenv()

DATABASE_URL = os.getenv("URI_MYSQL")

Base = declarative_base()

class SummaryDataOrm(Base):
    __tablename__ = os.getenv("UNIMED_TABLE_URLS")

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    url = Column(String(220), nullable=False)
    latitude = Column(String(32), nullable=False)
    longitude = Column(String(32), nullable=False)
    numero_pagina = Column(Integer, nullable=False)
    plano = Column(String(32), primary_key=True, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=None)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'plano'),
    )

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class SummaryDataRepository:
    def save_url_crawled(self, item: SummaryDataOrm):

        urls_crawled_orm = SummaryDataOrm(**item.model_dump())

        db = SessionLocal()
        try:
            db.add(urls_crawled_orm)
            db.commit()
            db.refresh(urls_crawled_orm)
            return urls_crawled_orm
        finally:
            db.close()

    def update_url_crawled(self, id: int, item: SummaryDataOrm):
        db = SessionLocal()

        try:
            record = db.query(SummaryDataOrm).filter(SummaryDataOrm.id == id).first()
            if record:
                for key, value in item.dict(exclude_unset=True).items():
                    setattr(record, key, value)
                db.commit()
                db.refresh(record)

            return record
        finally:
            db.close()

    def get_url(self, url_data: dict):
        db = SessionLocal()
        try:
            return db.query(SummaryDataOrm).filter(
                SummaryDataOrm.url == url_data['url'],
                SummaryDataOrm.plano == url_data['plano'],
                SummaryDataOrm.latitude == url_data['latitude'],
                SummaryDataOrm.longitude == url_data['longitude'],
                SummaryDataOrm.numero_pagina == url_data['numero_pagina']
            ).first()
        finally:
            db.close()

    def get_urls_range_date(self, days = 5):
        db = SessionLocal()
        try:
            five_days_ago = datetime.now() - timedelta(days=days)
            return db.query(SummaryDataOrm).filter(
                or_(
                    and_(
                        SummaryDataOrm.created_at <= five_days_ago.strftime('%Y-%m-%d %H:%M:%S'),
                        SummaryDataOrm.updated_at == None
                    ),
                    SummaryDataOrm.updated_at <= five_days_ago.strftime('%Y-%m-%d %H:%M:%S')
                )
            ).all()

        finally:
            db.close()
