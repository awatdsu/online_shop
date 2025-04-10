"""
Модели бд
"""
import uuid
import datetime

from sqlalchemy import Float, String, text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncAttrs

class Base(AsyncAttrs, DeclarativeBase):
    pass

# class Product(Base):
#     __tablename__ = "products"
    
#     id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) 
#     product_name: Mapped[str] = mapped_column(String(50), nullable=False)
#     product_price: Mapped[float] = mapped_column(Float(), nullable=False)
#     product_description: Mapped[str] = mapped_column(String(100), nullable=False)
#     product_category: Mapped[str] = mapped_column(String(100), nullable=False)
    
#     product_merchant: Mapped["Merchant"] = relationship("Merchant", back_populates="merchant_products")

# class Cart(Base):
#     __tablename__ = "cart"
    
#     id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     cart_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
#     cart_products: Mapped[list["Product"]]
#     cart_user: Mapped["User"] = relationship("User", back_populates="cart")

# class Merchant(Base):
#     __tablename__ = "merchants"

#     id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     merchant_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
#     merchant_products: Mapped[list["Product"]] = relationship("Product", back_populates="merchant_name")

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) 
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(), unique=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(), unique=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime.datetime]   = mapped_column(server_default=text("TIMEZONE('utc',now())"))
    password: Mapped[str] = mapped_column(String(256), nullable=False)

    is_user: Mapped[bool] = mapped_column(default=True, server_default=text('true'), nullable=False)
    is_merchant: Mapped[bool] = mapped_column(default=False, server_default=text('false'), nullable=False)
    is_moderator: Mapped[bool] = mapped_column(default=False, server_default=text('false'), nullable=False)
    is_admin: Mapped[bool] = mapped_column(default=False, server_default=text('false'), nullable=False)

    # cart: Mapped["Cart"] = relationship("Cart", back_populates="cart_user")
    # def __repr__(self) -> str:
    #     return f"<User(id={self.id}, username={self.username}, tasks={self.tasks})>"

# class Category(Base):
#     __tablename__ = "categories"
    
#     id: Mapped[int] = mapped_column(primary_key=True)
#     category_name: Mapped[str] = mapped_column(String(30), nullable=False)
