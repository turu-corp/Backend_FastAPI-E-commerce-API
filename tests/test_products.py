"""
Product Tests
Tests for product CRUD operations
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
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_products.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

# override the get_db dependency
def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# Fixtures for test data
@pytest.fixture(scope="module")
def setup_test_data():
    """Setup test data before tests"""
    db = TestingSessionLocal()
    
    # Create role
    role = Role(id=uuid.uuid4(), name="customer")
    db.add(role)
    db.commit()
    
    # Create test user
    user = User(
        id=uuid.uuid4(),
        role_id=role.id,
        name="Test User",
        email="testproduct@example.com",
        password=get_password_hash("testpass123")
    )
    db.add(user)
    
    # Create test brand
    brand = Brand(id=uuid.uuid4(), name="Test Brand", country="Test Country")
    db.add(brand)
    
    # Create test category
    category = Category(id=uuid.uuid4(), name="Test Category", slug="test-category", parent_id=None)
    db.add(category)
    
    db.commit()
    
    brand_id = str(brand.id)
    category_id = str(category.id)
    
    db.close()
    
    yield {"brand_id": brand_id, "category_id": category_id}
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)

# Helper function to get auth token
def get_auth_token():
    """Helper function to get authentication token"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "testproduct@example.com",
            "password": "testpass123"
        }
    )
    return response.json()["access_token"]

# Test cases
def test_get_products_empty():
    """Test getting products when none exist"""
    response = client.get("/api/v1/products/")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# Test creating product
def test_create_product_unauthorized(setup_test_data):
    """Test creating product without authentication"""
    response = client.post(
        "/api/v1/products/",
        json={
            "name": "Test Product",
            "slug": "test-product",
            "description": "Test description",
            "brand_id": setup_test_data["brand_id"],
            "category_id": setup_test_data["category_id"]
        }
    )
    
    assert response.status_code == 401

# Test creating product
def test_create_product_success(setup_test_data):
    """Test creating product with authentication"""
    token = get_auth_token()
    
    response = client.post(
        "/api/v1/products/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Test Product",
            "slug": "test-product",
            "description": "Test description",
            "brand_id": setup_test_data["brand_id"],
            "category_id": setup_test_data["category_id"],
            "images": [
                {
                    "image_url": "https://example.com/image.jpg",
                    "is_thumbnail": True
                }
            ],
            "variants": [
                {
                    "sku": "TEST-001",
                    "price_adjustment": 100000,
                    "stock": 50
                }
            ]
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Product"
    assert data["slug"] == "test-product"
    assert len(data["images"]) == 1
    assert len(data["variants"]) == 1

# Testing duplicate slug
def test_create_product_duplicate_slug(setup_test_data):
    """Test creating product with duplicate slug"""
    token = get_auth_token()
    
    # Create first product
    client.post(
        "/api/v1/products/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "First Product",
            "slug": "duplicate-slug",
            "description": "First product",
            "brand_id": setup_test_data["brand_id"],
            "category_id": setup_test_data["category_id"]
        }
    )
    
    # Try to create with same slug
    response = client.post(
        "/api/v1/products/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Second Product",
            "slug": "duplicate-slug",
            "description": "Second product",
            "brand_id": setup_test_data["brand_id"],
            "category_id": setup_test_data["category_id"]
        }
    )
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()

# Testing get product by ID
def test_get_product_by_id(setup_test_data):
    """Test getting product by ID"""
    token = get_auth_token()
    
    # Create product
    create_response = client.post(
        "/api/v1/products/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Get By ID Product",
            "slug": "get-by-id-product",
            "description": "Test",
            "brand_id": setup_test_data["brand_id"],
            "category_id": setup_test_data["category_id"]
        }
    )
    
    product_id = create_response.json()["id"]
    
    # Get product
    response = client.get(f"/api/v1/products/{product_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    assert data["name"] == "Get By ID Product"

# Test getting product by slug
def test_get_product_by_slug(setup_test_data):
    """Test getting product by slug"""
    token = get_auth_token()
    
    # Create product
    client.post(
        "/api/v1/products/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Get By Slug Product",
            "slug": "get-by-slug",
            "description": "Test",
            "brand_id": setup_test_data["brand_id"],
            "category_id": setup_test_data["category_id"]
        }
    )
    
    # Get product by slug
    response = client.get("/api/v1/products/slug/get-by-slug")
    
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "get-by-slug"

# Testing updating product
def test_update_product(setup_test_data):
    """Test updating product"""
    token = get_auth_token()
    
    # Create product
    create_response = client.post(
        "/api/v1/products/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Update Product",
            "slug": "update-product",
            "description": "Original",
            "brand_id": setup_test_data["brand_id"],
            "category_id": setup_test_data["category_id"]
        }
    )
    
    product_id = create_response.json()["id"]
    
    # Update product
    response = client.put(
        f"/api/v1/products/{product_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Updated Product",
            "description": "Updated description"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Product"
    assert data["description"] == "Updated description"

# Testing deleting product
def test_delete_product(setup_test_data):
    """Test deleting product"""
    token = get_auth_token()
    
    # Create product
    create_response = client.post(
        "/api/v1/products/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Delete Product",
            "slug": "delete-product",
            "description": "To be deleted",
            "brand_id": setup_test_data["brand_id"],
            "category_id": setup_test_data["category_id"]
        }
    )
    
    product_id = create_response.json()["id"]
    
    # Delete product
    response = client.delete(
        f"/api/v1/products/{product_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 204
    
    # Verify deletion
    get_response = client.get(f"/api/v1/products/{product_id}")
    assert get_response.status_code == 404

# Testing search products
def test_search_products(setup_test_data):
    """Test searching products"""
    token = get_auth_token()
    
    # Create products
    client.post(
        "/api/v1/products/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "iPhone 15 Pro",
            "slug": "iphone-15-pro",
            "description": "Apple smartphone",
            "brand_id": setup_test_data["brand_id"],
            "category_id": setup_test_data["category_id"]
        }
    )
    
    # Search
    response = client.get("/api/v1/products/?search=iphone")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "iphone" in data[0]["name"].lower()

# Testing pagination
def test_pagination(setup_test_data):
    """Test product pagination"""
    token = get_auth_token()
    
    # Create multiple products
    for i in range(5):
        client.post(
            "/api/v1/products/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": f"Product {i}",
                "slug": f"product-{i}",
                "description": f"Description {i}",
                "brand_id": setup_test_data["brand_id"],
                "category_id": setup_test_data["category_id"]
            }
        )
    
    # Test pagination
    response = client.get("/api/v1/products/?skip=0&limit=3")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 3