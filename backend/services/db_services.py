from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from backend.config import DATABASE_URL

# Create the database engine.
# pool_pre_ping: verify each pooled connection is alive before use, so
#   connections dropped by MySQL's wait_timeout are transparently replaced.
# pool_recycle: proactively retire connections older than 1h, well below
#   MySQL's wait_timeout (28800s), so idle connections never go stale.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
