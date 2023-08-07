from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel

# Define the database connection
DATABASE_URL = "sqlite:///mydatabase.db"
engine = create_engine(DATABASE_URL, echo=True)
SessionsLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

# Pydantic model for the item
class WebhookPayload(BaseModel):
    ref: str
    before: str
    after: str
    repository: dict
    pusher: dict
    commits: list

# Define a base class for declarative models
Base = declarative_base()

# Model for the database
class WebhookPayloadCreate(Base):
    __tablename__ = "webhook_payloads"

    id = Column(Integer, primary_key=True, index=True)
    ref = Column(String)
    before = Column(String)
    after = Column(String)
    repository_name = Column(String)
    repository_full_name = Column(String)
    pusher_name = Column(String)
    commit_id = Column(String)
    commit_message = Column(String)
    # commit_timestamp = Column(DateTime)
    commit_url = Column(String)
    commit_author_name = Column(String)
    commit_author_email = Column(String)

# Create an item
@app.post("/webhook")
def create_webhook(payload: WebhookPayload):
    try:
        db_payload = WebhookPayloadCreate(
            ref=payload.ref,
            before=payload.before,
            after=payload.after,
            repository_name=payload.repository["name"],
            repository_full_name=payload.repository["full_name"],
            pusher_name=payload.pusher["name"],
            commit_id=payload.commits[0]["id"],
            commit_message=payload.commits[0]["message"],
            # commit_timestamp=datetime.strptime(payload.commits[0]["timestamp"], "%Y-%m-%dT%H:%M:%SZ"),
            commit_url=payload.commits[0]["url"],
            commit_author_name=payload.commits[0]["author"]["name"],
            commit_author_email=payload.commits[0]["author"]["email"]
        )
        
        db = SessionsLocal()
        db.add(db_payload)
        db.commit()
        db.refresh(db_payload)
        db.close()
        
        # Write payload to file for debug purposes
        debug(payload)
        
        return db_payload
        
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error processing webhook")

# Get all data
@app.get("/data")
def read_data(skip: int = 0, limit: int = 10):
    try:
        db = SessionsLocal()
        data = db.query(WebhookPayloadCreate).offset(skip).limit(limit).all()
        db.close()
        return data

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error processing webhook")

# Hello World
@app.get("/")
async def root():
    return {"message": "Hello World"}

# Write payload to file for debug purposes
import json
def debug(payload: WebhookPayload):
    file_path = "/home/luiss/webhook.json"
    with open(file_path, 'w') as json_file:
        json.dump(payload.dict(), json_file, indent=4)
        
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)