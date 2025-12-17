from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.utils.security import pwd_context, create_access_token
from pydantic import EmailStr, ValidationError, TypeAdapter
from app.models.user import Role, User  # Path impor baru
from app.schemas.user import UserCreate, UserRead # Path impor baru
from app.schemas.auth import Token # Skema baru untuk token
from app.database import get_db, SessionLocal
from app.services import EmailService

router = APIRouter()


@router.post("/register", response_model=UserRead)
def register(user: UserCreate, session: SessionLocal = Depends(get_db)): # type: ignore
    # Check if user already exists
    existing_user = session.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Get or create default role
    role = session.query(Role).filter(Role.name == "customer").first()
    if not role:
        role = Role(name="customer")
        session.add(role)
        session.commit()
        session.refresh(role)

    hashed = pwd_context.hash(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hashed,
        role_id=role.id
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    # Panggil fungsi pengirim email dari service layer
    # EmailService.send_welcome_email(email=db_user.email, name=db_user.name)

    return db_user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: SessionLocal = Depends(get_db)): # type: ignore
    try:
        # 1. Validasi format email dan konversi ke lowercase
        email_adapter = TypeAdapter(EmailStr)
        email = email_adapter.validate_python(form_data.username.lower())
    except ValidationError:
        raise HTTPException(
            status_code=400,
            detail="Invalid email format for username",
        )

    # 2. Cari user berdasarkan email lowercase
    db_user = session.query(User).filter(User.email == email).first()

    # 3. Verifikasi user dan password
    if not db_user or not pwd_context.verify(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token(data={"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}
