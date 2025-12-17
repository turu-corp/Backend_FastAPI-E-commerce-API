import uuid
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel, Column, TEXT

from app.models.user import User
from .base import TimeStampedModel

# Brand, Category, Product, ProductImage, ProductVariant, Review, Attribute, AttributeValue, VariantAttributeValue Models
class Brand(TimeStampedModel, table=True):
    __tablename__ = "brands"
    name: str = Field(max_length=255, nullable=False)
    country: str = Field(max_length=255, nullable=False)
    products: List["Product"] = Relationship(back_populates="brand")

class Category(TimeStampedModel, table=True):
    __tablename__ = "categories"
    parent_id: Optional[uuid.UUID] = Field(default=None, foreign_key="categories.id")
    name: str = Field(max_length=255, nullable=False)
    slug: str = Field(max_length=255, unique=True, nullable=False)

    parent: Optional["Category"] = Relationship(back_populates="children", sa_relationship_kwargs=dict(remote_side="Category.id"))
    children: List["Category"] = Relationship(back_populates="parent")
    products: List["Product"] = Relationship(back_populates="category")

class Product(TimeStampedModel, table=True):
    __tablename__ = "products"
    brand_id: uuid.UUID = Field(foreign_key="brands.id")
    category_id: uuid.UUID = Field(foreign_key="categories.id")
    name: str = Field(max_length=255, nullable=False)
    slug: str = Field(max_length=255, unique=True, nullable=False)
    description: Optional[str] = Field(sa_column=Column(TEXT), default=None)

    brand: Brand = Relationship(back_populates="products")
    category: Category = Relationship(back_populates="products")
    images: List["ProductImage"] = Relationship(back_populates="product")
    variants: List["ProductVariant"] = Relationship(back_populates="product")
    reviews: List["Review"] = Relationship(back_populates="product")

class ProductImage(TimeStampedModel, table=True):
    __tablename__ = "product_images"
    product_id: uuid.UUID = Field(foreign_key="products.id")
    image_url: str = Field(max_length=255, nullable=False)
    is_thumbnail: bool = Field(default=False)

    product: Product = Relationship(back_populates="images")

class ProductVariant(TimeStampedModel, table=True):
    __tablename__ = "product_variants"
    product_id: uuid.UUID = Field(foreign_key="products.id")
    sku: str = Field(max_length=255, unique=True, nullable=False)
    price_adjustment: int = Field(default=0)
    stock: int = Field(default=0)

    product: Product = Relationship(back_populates="variants")
    attribute_values: List["VariantAttributeValue"] = Relationship(back_populates="variant")

class Review(TimeStampedModel, table=True):
    __tablename__ = "reviews"
    user_id: uuid.UUID = Field(foreign_key="users.id")
    product_id: uuid.UUID = Field(foreign_key="products.id")
    rating: int
    comment: Optional[str] = Field(sa_column=Column(TEXT), default=None)

    user: "User" = Relationship(back_populates="reviews")
    product: Product = Relationship(back_populates="reviews")

class Attribute(TimeStampedModel, table=True):
    __tablename__ = "attributes"
    name: str = Field(max_length=255, nullable=False)
    type: str = Field(max_length=255, nullable=False)
    values: List["AttributeValue"] = Relationship(back_populates="attribute")

class AttributeValue(TimeStampedModel, table=True):
    __tablename__ = "attribute_values"
    attribute_id: uuid.UUID = Field(foreign_key="attributes.id")
    value: str = Field(max_length=255, nullable=False)

    attribute: Attribute = Relationship(back_populates="values")
    variant_values: List["VariantAttributeValue"] = Relationship(back_populates="attribute_value")

class VariantAttributeValue(TimeStampedModel, table=True):
    __tablename__ = "variant_attribute_values"
    variant_id: uuid.UUID = Field(foreign_key="product_variants.id")
    attribute_value_id: uuid.UUID = Field(foreign_key="attribute_values.id")

    variant: ProductVariant = Relationship(back_populates="attribute_values")
    attribute_value: AttributeValue = Relationship(back_populates="variant_values")
