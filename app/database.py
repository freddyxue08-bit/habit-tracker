import os

from sqlmodel import Session, SQLModel, create_engine

# Locally this is a file next to the code. On a host you can point it
# somewhere persistent by setting the DATABASE_URL environment variable.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///habits.db")

# check_same_thread=False lets FastAPI use the SQLite connection across threads.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency: gives each request its own database session."""
    with Session(engine) as session:
        yield session
