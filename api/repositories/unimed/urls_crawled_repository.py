from sqlalchemy import create_engine, Column, BigInteger, String, Integer, Boolean, DateTime, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("URL_MYSQL_UNIMED")

Base = declarative_base()

class URLsCrawled(Base):
    __tablename__ = os.getenv("UNIMED_TABLE_URLS")

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    url = Column(String(220), nullable=False)
    latitude = Column(String(16), nullable=False)
    longitude = Column(String(16), nullable=False)
    numero_pagina = Column(Integer, nullable=False)
    plano = Column(String(32), primary_key=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), default=None)

    __table_args__ = (
        PrimaryKeyConstraint('id', 'plano'),
    )

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class URLsCrawledRepository:
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
            return db.query(URLsCrawled).filter(URLsCrawled.id == item_id).first()
        finally:
            db.close()

    def get_items(self):
        db = SessionLocal()
        try:
            return db.query(URLsCrawled).all()
        finally:
            db.close()