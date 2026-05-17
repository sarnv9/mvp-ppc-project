from sqlalchemy import create_engine, Column, String, Integer, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv(override=True)

#URL_DATABASE = os.getenv("DATABASE_URL")
#engine = create_engine(URL_DATABASE)

ADMIN_URL = os.getenv("ADMIN_DATABASE_URL")
admin_engine = create_engine(ADMIN_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=admin_engine)
Base = declarative_base()

#def init_db():
#    Base.metadata.create_all(bind=engine)


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


#def init_db():       Base.metadata.create_all(bind=engine)