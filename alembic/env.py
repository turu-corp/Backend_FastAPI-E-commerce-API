# alembic/env.py

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from sqlmodel import SQLModel 
from app.models import * 
from app.config import settings 

target_metadata = SQLModel.metadata 


# ...
