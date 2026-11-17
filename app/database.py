from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = "sqlite:///habits.db"

# check_same_thread=False lets FastAPI use the SQLite connection across threads.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency: gives each request its own database session."""
    with Session(engine) as session:
        yield session
