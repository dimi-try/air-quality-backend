from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from app.db.models import Base
from config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    echo=False,  # Отвечает за вывод логов
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
    )

Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()
