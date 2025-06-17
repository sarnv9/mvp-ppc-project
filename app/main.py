from fastapi import FastAPI, UploadFile, File
import pandas as pd
from sqlalchemy.orm import sessionmaker
from app.database import engine
from app.models import Campaign

app = FastAPI()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@app.post("/submit_campaign/")
async def submit_campaign(file: UploadFile = File(...)):
    df = pd.read_csv(file.file)
    
    session = SessionLocal()
    for _, row in df.iterrows():
        campaign = Campaign(
            name=row['name'],
            clicks=row['clicks'],
            conversions=row['conversions'],
            cost=row['cost'],
            revenue=row['revenue']
        )
        session.add(campaign)
    session.commit()
    session.close()
    
    return {"message": "Campaign data uploaded!"}

@app.get("/view_campaign_metrics/")
def view_campaign_metrics():
    session = SessionLocal()
    campaigns = session.query(Campaign).all()
    session.close()
    
    return {"data": [c.__dict__ for c in campaigns]}
