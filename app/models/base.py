import uuid
from sqlmodel import Field, SQLModel
from datetime import datetime

class BaseUUIDModel(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

class TimeStampedModel(BaseUUIDModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
