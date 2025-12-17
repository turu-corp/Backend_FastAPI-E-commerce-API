"""
Middleware package
Custom middleware for the application
"""

from app.middleware.logging import LoggingMiddleware

__all__ = ["LoggingMiddleware"]