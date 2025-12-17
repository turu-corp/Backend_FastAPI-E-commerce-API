# alembic/env.py

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from sqlmodel import SQLModel # Impor SQLModel
from app.models import * # Impor semua model Anda
from app.config import settings # Impor settings Anda

# target_metadata = None
target_metadata = SQLModel.metadata # Hanya gunakan metadata dari SQLModel


# ...
