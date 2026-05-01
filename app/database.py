from sqlalchemy import create_engine, Column, String, Integer, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

URL_DATABASE = os.getenv("DATABASE_URL")

engine = create_engine(URL_DATABASE)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class PerformanceMetric(Base):
    __tablename__ = 'performance_metrics'

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String)  # 'google' or 'meta'
    campaign = Column(String)
    date = Column(Date)       
    cost = Column(Float)
    revenue = Column(Float)
    conversions = Column(Integer)
    impressions = Column(Integer)
    clicks = Column(Integer)
    roi = Column(Float)
    roas = Column(Float)
    cpa = Column(Float)
    cvr = Column(Float)
    cpc = Column(Float)


def init_db():
    Base.metadata.create_all(bind=engine)