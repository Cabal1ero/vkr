from ninja import Schema
from typing import List, Optional, Any

class CategorySchema(Schema):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    image: Optional[str] = None
    parent_id: Optional[int] = None

class ProductImageSchema(Schema):
    id: int
    image: str
    is_main: bool

class ProductListSchema(Schema):
    id: int
    name: str
    price: float
    original_price: Optional[float] = None
    rating: float
    reviews_count: int
    in_stock: bool
    main_image: Optional[ProductImageSchema] = None

class ProductDetailSchema(Schema):
    id: int
    name: str
    description: str
    price: float
    original_price: Optional[float] = None
    category: CategorySchema
    brand: str
    model: str
    specifications: Any # JSONField
    features: List[Any] # JSONField
    in_stock: bool
    rating: float
    reviews_count: int
    images: List[ProductImageSchema]

class CartProductSchema(Schema):
    id: int
    name: str
    price: float
    image: Optional[str] = None # Assuming a simple image URL is enough here

class CartItemSchema(Schema):
    id: int
    product: CartProductSchema
    quantity: int

class CartSchema(Schema):
    items: List[CartItemSchema]
    total: float

# Schemas for Orders
class OrderItemSchema(Schema):
    id: int
    product_name: str
    quantity: int
    price: float

class OrderSchema(Schema):
    id: int
    order_number: str
    status: str
    first_name: str
    last_name: str
    email: str
    phone: str
    city: str
    address: str
    apartment: Optional[str]
    postal_code: str
    delivery_method: str
    payment_method: str
    comment: Optional[str]
    total_amount: float
    delivery_fee: float
    created_at: str
    items: List[OrderItemSchema]

class OrderListSchema(Schema):
    id: int
    order_number: str
    status: str
    total_amount: float
    created_at: str

class CreateOrderSchema(Schema):
    first_name: str
    last_name: str
    email: str
    phone: str
    city: str
    address: str
    apartment: Optional[str] = None
    postal_code: str
    delivery_method: str
    payment_method: str
    comment: Optional[str] = None 