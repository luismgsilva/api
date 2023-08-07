from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the database connection
DATABASE_URL = "sqlite:///mydatabase.db"
engine = create_engine(DATABASE_URL, echo=True)
SessionsLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative models
Base = declarative_base()

# Define a sample model
class WebhookPayload(Base):
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
    
# Create the database tables
Base.metadata.create_all(bind=engine)