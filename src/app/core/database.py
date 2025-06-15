from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

SQLALCHEMY_DATABASE_URL = "postgresql://rds_fastapi_dev:music-password@rds-fastapi-dev.cgdemwa0uf7v.us-east-1.rds.amazonaws.com:5432/musicdb"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"options": "-csearch_path=vibesia_schema"}
)

SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine,
    expire_on_commit=False
)
Base = declarative_base()

def create_table():

    Base.metadata.schema = "vibesia_schema"
    Base.metadata.create_all(bind=engine)