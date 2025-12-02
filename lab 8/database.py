from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = (
    "mssql+pyodbc://@(localdb)\\MSSQLLocalDB/wyporzyczalnia?"
    "driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
