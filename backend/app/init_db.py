"""Create all database tables. Run: python -m app.init_db"""
from app.database import Base, engine
from app import models  # noqa: F401  (ensures models are registered)


def main() -> None:
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")


if __name__ == "__main__":
    main()
