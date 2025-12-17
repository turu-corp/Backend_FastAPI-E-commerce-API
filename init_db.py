#!/usr/bin/env python3
"""
Script to initialize the database tables.
"""
from app.database import init_db

if __name__ == "__main__":
    init_db()
    print("Database tables created successfully!")
