from sqlalchemy import create_engine
from pathlib import Path
from sqlalchemy.orm import declarative_base, sessionmaker

# SQLite database file path (will be created in your project root)
# .parent (core) -> .parent (speechfix) -> .parent (InterviewIQ root)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# This creates an absolute path to InterviewIQ/interviewiq.db
SQLALCHEMY_DATABASE_URL = f"sqlite:///{BASE_DIR}/interviewiq.db"


# check_same_thread=False is needed only for SQLite in FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency to get the DB session in your routers
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
