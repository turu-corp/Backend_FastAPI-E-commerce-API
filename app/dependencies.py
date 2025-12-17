"""
Shared dependencies untuk aplikasi
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional
import uuid

import logging # Import logging
from app.database import get_db
from app.models.user import User, Role
from app.utils.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# user role-based dependencies
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency untuk mendapatkan current authenticated user dari JWT token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    try:
        user = db.query(User).filter(User.email == email).first()
    except ValueError:
        raise credentials_exception
    
    if user is None:
        raise credentials_exception
    
    return user

# Dependency to ensure the user is active
def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency untuk memastikan user aktif
    Bisa ditambahkan pengecekan is_active field jika ada
    """
    return current_user

# Role-based access control dependency factory  
def require_role(allowed_roles: list):
    """
    Dependency factory untuk role-based access control
    
    Usage:
        @router.get("/admin")
        def admin_only(user: User = Depends(require_role(["admin"]))):
            ...
    """
    def role_checker(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        # --- DEBUGGING LOGS ---
        logging.info(f"--- Role Check for user: {current_user.email} (User ID: {current_user.id}) ---")
        logging.info(f"User's role_id from DB is: {current_user.role_id}")

        # Access the role directly through the relationship
        user_role = current_user.role

        if user_role:
            logging.info(f"Role object accessed via relationship: '{user_role.name}'")
        else:
            # This would indicate a problem with the SQLAlchemy relationship loading
            logging.error(f"!!! CRITICAL: Could not access user.role relationship for user {current_user.email} !!!")
        
        # Make the check case-insensitive and strip whitespace
        is_allowed = user_role and user_role.name.lower().strip() in allowed_roles

        if not is_allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this resource"
            )
        return current_user
    return role_checker

# Convenience dependencies
get_admin_user = require_role(["admin"])
get_customer_user = require_role(["customer", "admin"])