"""
Seed initial data to database
Run: python seed.py
"""
from app.database import get_session
from app.models.user import Role
from app.models.product import Brand, Category
from app.models.order import Discount
from datetime import datetime, timedelta
import uuid

def seed_roles():
    """Create initial roles"""
    db = SessionLocal() # type: ignore
    
    roles_data = [
        {"name": "admin"},
        {"name": "customer"},
        {"name": "vendor"}
    ]
    
    for role_data in roles_data:
        existing = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not existing:
            role = Role(id=uuid.uuid4(), **role_data)
            db.add(role)
            print(f"✓ Created role: {role_data['name']}")
    
    print("✅ Roles seeded successfully!\n")


def seed_brands():
    """Create sample brands"""
    db = SessionLocal() # type: ignore
    
    brands_data = [
        {"name": "Apple", "country": "USA"},
        {"name": "Samsung", "country": "South Korea"},
        {"name": "Sony", "country": "Japan"},
        {"name": "Nike", "country": "USA"},
        {"name": "Adidas", "country": "Germany"},
        {"name": "Dell", "country": "USA"},
        {"name": "HP", "country": "USA"},
        {"name": "Asus", "country": "Taiwan"},
    ]
    
    for brand_data in brands_data:
        existing = db.query(Brand).filter(Brand.name == brand_data["name"]).first()
        if not existing:
            brand = Brand(id=uuid.uuid4(), **brand_data)
            db.add(brand)
            print(f"✓ Created brand: {brand_data['name']}")
    
    db.commit()
    db.close()
    print("✅ Brands seeded successfully!\n")


def seed_categories():
    """Create sample categories with hierarchy"""
    db = SessionLocal() # type: ignore
    
    # Root categories
    root_categories = [
        {"name": "Electronics", "slug": "electronics"},
        {"name": "Clothing", "slug": "clothing"},
        {"name": "Books", "slug": "books"},
        {"name": "Sports", "slug": "sports"},
        {"name": "Home & Garden", "slug": "home-garden"},
    ]
    
    created_roots = {}
    
    for cat_data in root_categories:
        existing = db.query(Category).filter(Category.slug == cat_data["slug"]).first()
        if not existing:
            category = Category(id=uuid.uuid4(), parent_id=None, **cat_data)
            db.add(category)
            db.flush()
            created_roots[cat_data["name"]] = category.id
            print(f"✓ Created category: {cat_data['name']}")
        else:
            created_roots[cat_data["name"]] = existing.id
    
    # Sub categories
    electronics_id = created_roots.get("Electronics")
    clothing_id = created_roots.get("Clothing")
    sports_id = created_roots.get("Sports")
    
    sub_categories = [
        {"name": "Smartphones", "slug": "smartphones", "parent_id": electronics_id},
        {"name": "Laptops", "slug": "laptops", "parent_id": electronics_id},
        {"name": "Tablets", "slug": "tablets", "parent_id": electronics_id},
        {"name": "Men's Clothing", "slug": "mens-clothing", "parent_id": clothing_id},
        {"name": "Women's Clothing", "slug": "womens-clothing", "parent_id": clothing_id},
        {"name": "Shoes", "slug": "shoes", "parent_id": clothing_id},
        {"name": "Gym Equipment", "slug": "gym-equipment", "parent_id": sports_id},
        {"name": "Outdoor Sports", "slug": "outdoor-sports", "parent_id": sports_id},
    ]
    
    for cat_data in sub_categories:
        if cat_data["parent_id"]:  # Only create if parent exists
            existing = db.query(Category).filter(Category.slug == cat_data["slug"]).first()
            if not existing:
                category = Category(id=uuid.uuid4(), **cat_data)
                db.add(category)
                print(f"  ✓ Created subcategory: {cat_data['name']}")
    
    db.commit()
    db.close()
    print("✅ Categories seeded successfully!\n")


def seed_discounts():
    """Create sample discount codes"""
    db = SessionLocal() # type: ignore
    
    now = datetime.utcnow()
    
    discounts_data = [
        {
            "code": "WELCOME10",
            "type": "percentage",
            "amount": 10,
            "min_purchase": 100000,
            "start_date": now,
            "end_date": now + timedelta(days=30)
        },
        {
            "code": "FREESHIP",
            "type": "fixed",
            "amount": 15000,
            "min_purchase": 200000,
            "start_date": now,
            "end_date": now + timedelta(days=60)
        },
        {
            "code": "MEGA50",
            "type": "percentage",
            "amount": 50,
            "min_purchase": 500000,
            "start_date": now,
            "end_date": now + timedelta(days=7)
        },
    ]
    
    for discount_data in discounts_data:
        existing = db.query(Discount).filter(Discount.code == discount_data["code"]).first()
        if not existing:
            discount = Discount(id=uuid.uuid4(), **discount_data)
            db.add(discount)
            print(f"✓ Created discount: {discount_data['code']} ({discount_data['type']} - {discount_data['amount']})")
    
    db.commit()
    db.close()
    print("✅ Discounts seeded successfully!\n")


def main():
    """Run all seeders"""
    print("\n" + "="*50)
    print("🌱 Starting database seeding...")
    print("="*50 + "\n")
    
    try:
        seed_roles()
        seed_brands()
        seed_categories()
        seed_discounts()
        
        print("\n" + "="*50)
        print("✅ All data seeded successfully!")
        print("="*50)
        print("\n📝 Next steps:")
        print("1. Register a user: POST /api/v1/auth/register")
        print("2. Login: POST /api/v1/auth/login")
        print("3. Create products: POST /api/v1/products/")
        print("4. Start shopping! 🛒\n")
        
    except Exception as e:
        print(f"\n❌ Error seeding data: {str(e)}")
        print("Make sure your database is running and configured correctly.\n")


if __name__ == "__main__":
    main()