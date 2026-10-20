import os
from dotenv import load_dotenv
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase,sessionmaker

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

BASE_DB_URL = (
    f"mysql+pymysql://{os.environ.get('DATABASE_USER')}:"
    f"{os.environ.get('DATABASE_USER_PASSWORD')}@"
    f"{os.environ.get('DATABASE_IP')}:"
    f"{os.environ.get('DATABASE_PORT')}/"
    f"{os.environ.get('DATABASE_NAME')}"
)

engine = create_engine(url=BASE_DB_URL, pool_size=10, pool_pre_ping=True, max_overflow=5)

session = sessionmaker(bind=engine,autoflush=False, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = session()
    try:
        yield db
    except Exception as e:
        print(f"ERROR: {e}")
        raise
    finally:
        db.close()