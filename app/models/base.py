import uuid
from sqlmodel import Field, SQLModel
from datetime import datetime

# Base model with UUID primary key
class BaseUUIDModel(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

# Timestamp mixin for created_at and updated_at fields
class TimeStampedModel(BaseUUIDModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
