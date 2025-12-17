"""
Logging Middleware
Logs all incoming requests and responses
"""

import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all HTTP requests and responses
    """
    
    async def dispatch(self, request: Request, call_next):
        # Start timer
        start_time = time.time()
        
        # Get request info
        method = request.method
        url = request.url.path
        client = request.client.host if request.client else "unknown"
        
        # Log request
        logger.info(f"Request: {method} {url} from {client}")
        
        # Process request
        try:
            response: Response = await call_next(request)
            
            # Calculate process time
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response: {method} {url} - "
                f"Status: {response.status_code} - "
                f"Time: {process_time:.3f}s"
            )
            
            # Add custom header with process time
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            logger.error(
                f"Error: {method} {url} - "
                f"Error: {str(e)} - "
                f"Time: {process_time:.3f}s"
            )
            raise