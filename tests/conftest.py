"""
Pytest Configuration
Shared fixtures for all tests
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models.user import Role, User
from app.models.product import Brand, Category
from app.utils.security import get_password_hash
import uuid

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency override
def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the dependency
app.dependency_overrides[get_db] = override_get_db

# Fixtures
@pytest.fixture(scope="session")
def db_engine():
    """Create database engine for tests"""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

# Fixture for database session
@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create a new database session for each test"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

# Fixture for test client
@pytest.fixture(scope="function")
def client():
    """Create test client"""
    return TestClient(app)

# Fixtures for test data
@pytest.fixture(scope="session")
def test_role(db_engine):
    """Create test role"""
    db = TestingSessionLocal()
    role = Role(id=uuid.uuid4(), name="customer")
    db.add(role)
    db.commit()
    role_id = role.id
    db.close()
    return role_id

# Fixture for test user
@pytest.fixture(scope="session")
def test_user(db_engine, test_role):
    """Create test user"""
    db = TestingSessionLocal()
    user = User(
        id=uuid.uuid4(),
        role_id=test_role,
        name="Test User",
        email="test@example.com",
        password=get_password_hash("testpass123")
    )
    db.add(user)
    db.commit()
    user_id = user.id
    db.close()
    return user_id

# Fixture for test brand
@pytest.fixture(scope="session")
def test_brand(db_engine):
    """Create test brand"""
    db = TestingSessionLocal()
    brand = Brand(id=uuid.uuid4(), name="Test Brand", country="Test Country")
    db.add(brand)
    db.commit()
    brand_id = brand.id
    db.close()
    return brand_id

# Fixture for test category
@pytest.fixture(scope="session")
def test_category(db_engine):
    """Create test category"""
    db = TestingSessionLocal()
    category = Category(
        id=uuid.uuid4(),
        name="Test Category",
        slug="test-category",
        parent_id=None
    )
    db.add(category)
    db.commit()
    category_id = category.id
    db.close()
    return category_id

# Fixture for authentication token
@pytest.fixture
def auth_token(client):
    """Get authentication token for tests"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpass123"
        }
    )
    return response.json()["access_token"]

# Fixture for authentication headers
@pytest.fixture
def auth_headers(auth_token):
    """Get authentication headers"""
    return {"Authorization": f"Bearer {auth_token}"}