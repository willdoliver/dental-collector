from sqlalchemy import create_engine, Column, BigInteger, String, Integer, Boolean, DateTime, PrimaryKeyConstraint
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
    def save_url_crawled(self, item):

        urls_crawled_orm = SummaryDataOrm(**item.model_dump())

        db = SessionLocal()
        try:
            db.add(urls_crawled_orm)
            db.commit()
            db.refresh(urls_crawled_orm)
            return urls_crawled_orm
        finally:
            db.close()
    
    def update_url(id, item):
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

    def get_urls(self):
        db = SessionLocal()
        try:
            five_days_ago = datetime.now() - timedelta(days=5)
            return db.query(SummaryDataOrm).filter(
                SummaryDataOrm.created_at < five_days_ago.strftime('%Y-%m-%d %H:%M:%S')
            )

        finally:
            db.close()