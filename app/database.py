from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from app.config import settings

# --- MODIFIED SECTION ---
# Get the base Database URL from settings
db_url = settings.DATABASE_URL

# This is a more robust way to ensure the session timezone is UTC for PostgreSQL.
# It appends the timezone setting directly to the connection URL.
# This avoids issues where `connect_args` might be ignored.
if db_url.startswith("postgresql"):
    # Ensure we don't add the options parameter if it's already there
    if 'options' not in db_url:
        # The value `-c TimeZone=UTC` needs to be URL-encoded.
        # `%20` is a space, `%3D` is '='.
        db_url += "?options=-c%20TimeZone%3DUTC"

# Create the SQLAlchemy engine
engine = create_engine(db_url)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Function to create all tables (for both SQLModel and SQLAlchemy Base)
def create_db_and_tables():
    # This will create tables for SQLModel models
    SQLModel.metadata.create_all(engine)

# Dependency to get a DB session
def get_db():
    """
    Database session dependency.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
