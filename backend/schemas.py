from pydantic import BaseModel
from typing import List, Optional

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

class OrderResponse(BaseModel):
    id: int
    total: float
    message: str
