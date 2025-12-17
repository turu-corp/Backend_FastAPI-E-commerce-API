from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1 import auth, products, brands, categories, cart, orders, users, discounts, shippings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    # E-commerce API 🛒
    
    Complete backend API for e-commerce platform with authentication, 
    product management, cart, orders, and automated email workflows.
    
    ## Features
    
    * **Authentication**: JWT-based login/registration with email automation
    * **Products**: Full CRUD operations with variants, images, and attributes
    * **Categories & Brands**: Organize products hierarchically
    * **Shopping Cart**: Add, update, remove items with stock validation
    * **Orders**: Complete checkout process with payment and shipping
    * **Reviews**: Rate and review products
    * **Discounts**: Apply coupon codes for orders
    * **Workflow Automation**: 
        - Welcome email on registration
        - Order confirmation email on checkout
    
    ## Authentication
    
    Most endpoints require JWT authentication. First register or login to get your token,
    then include it in the `Authorization` header as `Bearer <token>`.
    
    ## Getting Started
    
    1. **Register**: POST /api/v1/auth/register
    2. **Login**: POST /api/v1/auth/login (get your JWT token)
    3. **Browse Products**: GET /api/v1/products/
    4. **Add to Cart**: POST /api/v1/cart/items (requires auth)
    5. **Checkout**: POST /api/v1/orders/ (requires auth)
    
    ## Workflow Automation Examples
    
    - **User Registration**: Automatically sends welcome email ✉️
    - **Order Placed**: Automatically sends order confirmation email 📧
    - **Stock Management**: Automatically updates inventory after order
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API V1 Router ---
api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_v1_router.include_router(users.router, prefix="/users", tags=["Users"])
api_v1_router.include_router(products.router, prefix="/products", tags=["Products"])
api_v1_router.include_router(brands.router, prefix="/brands", tags=["Brands"])
api_v1_router.include_router(categories.router, prefix="/categories", tags=["Categories"])
api_v1_router.include_router(cart.router, prefix="/cart", tags=["Cart"])
api_v1_router.include_router(orders.router, prefix="/orders", tags=["Orders"])
api_v1_router.include_router(discounts.router, prefix="/discounts", tags=["Discounts (Admin)"])
api_v1_router.include_router(shippings.router, prefix="/shippings", tags=["Shippings (Admin)"])

app.include_router(api_v1_router)


@app.get("/", tags=["Root"])
def read_root():
    """
    Root endpoint - API health check
    """
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "running",
        "endpoints": {
            "authentication": "/api/v1/auth",
            "products": "/api/v1/products",
            "brands": "/api/v1/brands",
            "categories": "/api/v1/categories",
            "cart": "/api/v1/cart",
            "orders": "/api/v1/orders"
        }
    }


@app.get("/health", tags=["Root"])
def health_check():
    """
    Health check endpoint for monitoring
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Enable auto-reload in development
    )