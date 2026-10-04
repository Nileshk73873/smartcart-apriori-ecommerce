from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    is_admin: Optional[bool] = False

    class Config:

        from_attributes = True

class ProductBase(BaseModel):
    stock_code: str
    name: str
    price: float
    description: Optional[str] = None
    image_url: Optional[str] = None

class Product(ProductBase):
    id: int

    class Config:
        from_attributes = True

class CartItemAdd(BaseModel):
    product_id: int
    quantity: int = 1

class CartItemUpdate(BaseModel):
    product_id: int
    quantity: int

class CartItem(BaseModel):
    product: Product
    quantity: int
    subtotal: float

class CartSummary(BaseModel):
    items: List[CartItem]
    subtotal: float
    discount: float
    final_total: float
    applied_bundle_tier: Optional[str] = None
    savings_reason: Optional[str] = None

class OrderCreate(BaseModel):
    customer_name: str
    email: str
    address: str
    city: str
    postal_code: str
    user_id: Optional[int] = None

class OrderResponse(BaseModel):
    id: int
    total: float
    message: str

class OrderItemResponse(BaseModel):
    product: Product
    quantity: int
    price: float
    
    class Config:
        from_attributes = True

class FullOrderResponse(BaseModel):
    id: int
    customer_name: str
    email: str
    address: str
    city: str
    postal_code: str
    subtotal: float
    discount: float
    total: float
    status: str
    created_at: Optional[datetime] = None
    items: List[OrderItemResponse]
    
    class Config:
        from_attributes = True

class ReturnRequest(BaseModel):
    order_id: int
    reason: Optional[str] = None

class OrderStatusUpdate(BaseModel):
    status: str
