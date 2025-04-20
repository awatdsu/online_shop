"""
Модели бд
"""
from decimal import Decimal
import uuid
import datetime
from enum import Enum


from sqlalchemy import Boolean, Numeric, String, text, ForeignKey, Text#, ARRAY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncAttrs

class UserRole(str, Enum):
    USER = "user"
    MERCHANT = "merchant"
    MODERATOR = "moderator"
    ADMIN = "admin"

class OrderStatus(str, Enum):
    PENDING = "Pending" # created but not paid
    PROCESSING = "Processing" # paid and is being processed by merchant
    CANCELED = "Canceled"
    COMPLETED = "Completed"
    EXCEPTION = "Exception"

class FulfillmentStatus(str, Enum):
    UNFULFILLED = "Unfulfilled"
    FULFILLED = "Fulfilled"
    ON_HOLD = "On hold"

class ShipmentStatus(str, Enum):
    AWAITING_PICKUP = "Awaiting pickup"
    IN_TRANSIT = "In transit"
    DELAYED = "Delayed"
    OUT_FOR_DELIVERY = "Out for delivery"
    DELIVERED = "Delivered"
    AVAILABLE_FOR_PICKUP = "Available for pickup"
    EXCEPTION = "Exception"

class RatingEnum(int, Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10

class Base(AsyncAttrs, DeclarativeBase):
    pass

class Product(Base):
    __tablename__ = "products"
    
    id: Mapped[uuid.UUID]                           = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    product_name: Mapped[str]                       = mapped_column(String(50), nullable=False)
    product_price: Mapped[Decimal]                  = mapped_column(Numeric(10,2), nullable=False)
    product_description: Mapped[str]                = mapped_column(String(500), nullable=False)
    product_discount: Mapped[Decimal]               = mapped_column(Numeric(10,2), default=0)

    product_quantity: Mapped[int]                   = mapped_column(default=0)

    category_id: Mapped[int]                        = mapped_column(ForeignKey("categories.id"))
    category: Mapped["Category"] = relationship(
        "Category",
        back_populates="products",
        lazy="joined"
    )

    merchant_id: Mapped[uuid.UUID]                  = mapped_column(ForeignKey("merchants.id"))
    merchant: Mapped["Merchant"] = relationship(
        "Merchant", 
        back_populates="products"
    )

    comments: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="product",
        cascade="all, delete-orphan"
    )

    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="product",
        cascade="all, delete-orphan"
    )

class Merchant(Base):
    __tablename__ = "merchants"

    id: Mapped[uuid.UUID]                           = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_name: Mapped[str]                      = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str]                              = mapped_column(String(), unique=True, nullable=False)
    first_name: Mapped[str]                         = mapped_column(String(50), nullable=False)
    last_name: Mapped[str]                          = mapped_column(String(50), nullable=False)
    description: Mapped[str]                        = mapped_column(String(500), nullable=False)
    hashed_password: Mapped[str]                    = mapped_column(String(256), nullable=False)
    salt: Mapped[str]                               = mapped_column(String(32), nullable=False)
    is_active: Mapped[bool]                         = mapped_column(default=False, server_default=text('false'))
    
    created_at: Mapped[datetime.datetime]           = mapped_column(server_default=text("TIMEZONE('utc',now())"))

    
    products: Mapped[list["Product"]] = relationship(
        "Product", 
        back_populates="merchant", 
        cascade="all, delete-orphan"
    )

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID]                           = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) 
    username: Mapped[str]                           = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str]                              = mapped_column(String(), unique=True, nullable=False)
    phone_number: Mapped[str]                       = mapped_column(String(20), unique=True)
    first_name: Mapped[str]                         = mapped_column(String(50), nullable=False)
    last_name: Mapped[str]                          = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime.datetime]           = mapped_column(server_default=text("TIMEZONE('utc',now())"))
    password: Mapped[str]                           = mapped_column(String(256), nullable=False)

    is_blocked: Mapped[bool]                        = mapped_column(Boolean(), default=False)
    role: Mapped[UserRole]                          = mapped_column(default=UserRole.USER)

    orders: Mapped[list["Order"]] = relationship(
        "Order",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    # token: Mapped["UserToken"] = relationship(
    #     "UserToken",
    #     back_populates="user",
    #     cascade="all, delete-orphan"
    # )

# class UserToken(Base):
#     __tablename__ = "tokens"

#     id: Mapped[uuid.UUID]                           = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     refresh_token: Mapped[int]                      = mapped_column(String(), nullable=False)
#     devices: Mapped[list[str]]                      = mapped_column(ARRAY(String))

#     user_id: Mapped[uuid.UUID]                      = mapped_column(ForeignKey("users.id"))
#     user: Mapped["User"] = relationship(
#         "User",
#         back_populates="token"
#     )


class Category(Base):
    __tablename__ = "categories"
    
    id: Mapped[int]                                 = mapped_column(primary_key=True, autoincrement=True)
    category_name: Mapped[str]                      = mapped_column(String(30), nullable=False)
    
    products: Mapped[list["Product"]] = relationship(
        "Product", 
        back_populates="category", 
        cascade="all, delete-orphan"
    )

class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[uuid.UUID]                           = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content: Mapped[Text]                           = mapped_column(Text, nullable=True)
    rating: Mapped[RatingEnum]                      = mapped_column(default=RatingEnum.FIVE)
    created_at: Mapped[datetime.datetime]           = mapped_column(server_default=text("TIMEZONE('utc',now())"))

    user_id: Mapped[uuid.UUID]                      = mapped_column(ForeignKey('users.id'))
    user: Mapped["User"] = relationship(
        "User",
        back_populates="comments"
    )

    product_id: Mapped[uuid.UUID]                   = mapped_column(ForeignKey('products.id'))
    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="comments"
    )

class Order(Base):
    __tablename__ = "orders"
    
    id: Mapped[uuid.UUID]                           = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID]                      = mapped_column(ForeignKey("users.id"), nullable=False)
    order_date: Mapped[datetime.datetime]           = mapped_column(server_default=text("TIMEZONE('utc',now())"))
    updated_at: Mapped[datetime.datetime]           = mapped_column(server_default=text("TIMEZONE('utc',now())"), onupdate=text("TIMEZONE('utc',now())"))
    total_amount: Mapped[Decimal]                   = mapped_column(Numeric(10,2), nullable=False)
    status: Mapped[OrderStatus]                     = mapped_column(default=OrderStatus.PENDING)
    fulfillment_status: Mapped[FulfillmentStatus]   = mapped_column(default=FulfillmentStatus.UNFULFILLED)
    shipment_status: Mapped[ShipmentStatus]         = mapped_column(default=ShipmentStatus.AWAITING_PICKUP)
    shipping_address: Mapped[str]                   = mapped_column(Text, nullable=False)
    payment_method: Mapped[str]                     = mapped_column(String(50), nullable=False)
    transaction_id: Mapped[str]                     = mapped_column(String(100), unique=True)

    user: Mapped["User"] = relationship("User", back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", 
        back_populates="order",
        cascade="all, delete-orphan"
    )

class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[uuid.UUID]                           = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    order_id: Mapped[uuid.UUID]                     = mapped_column(ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[uuid.UUID]                   = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int]                           = mapped_column(default=1, nullable=False)
    price_at_purchase: Mapped[Decimal]                = mapped_column(Numeric(10,2), nullable=False)

    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product: Mapped["Product"] = relationship("Product", back_populates="order_items")
