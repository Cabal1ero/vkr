import uuid
from ninja import Router, Schema
from typing import List
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.conf import settings

from yookassa import Configuration, Payment

from shop.models import Order, OrderItem
from shop.utils import get_or_create_cart
from .schemas import CreateOrderSchema, OrderSchema, OrderListSchema

# Configure Yookassa
# В реальном проекте эти ключи должны быть в переменных окружения
Configuration.account_id = "YOUR_YOOKASSA_SHOP_ID" 
Configuration.secret_key = "YOUR_YOOKASSA_SECRET_KEY"

router = Router()

class CreateOrderResponseSchema(Schema):
    order_id: int
    confirmation_url: str

@router.post("", response={201: CreateOrderResponseSchema, 400: dict})
@transaction.atomic
def create_order(request, payload: CreateOrderSchema):
    """Create a new order from the cart."""
    cart = get_or_create_cart(request)
    cart_items = cart.items.all()

    if not cart_items.exists():
        return 400, {"message": "Cart is empty"}

    # Create the order
    order_data = payload.dict()
    if request.user.is_authenticated:
        order_data['user'] = request.user
    
    total_amount = sum(item.product.price * item.quantity for item in cart_items)
    # delivery_fee = ... # Логика расчета стоимости доставки
    
    order = Order.objects.create(
        **order_data,
        order_number=str(uuid.uuid4()),
        total_amount=total_amount
    )

    # Create order items
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            product_name=item.product.name,
            quantity=item.quantity,
            price=item.product.price
        )

    # Clear the cart
    cart.items.all().delete()

    # Create Yookassa payment
    payment = Payment.create({
        "amount": {
            "value": str(order.total_amount),
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "http://localhost:3000/orders/success" # URL на фронтенде
        },
        "capture": True,
        "description": f"Заказ №{order.order_number}",
        "metadata": {
            "order_id": order.id
        }
    }, uuid.uuid4())

    return 201, {"order_id": order.id, "confirmation_url": payment.confirmation.confirmation_url}


@router.get("", response=List[OrderListSchema])
def list_orders(request):
    """List orders for the current authenticated user."""
    if not request.user.is_authenticated:
        return 401, {"message": "Unauthorized"}
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return orders

@router.get("/{order_id}", response=OrderSchema)
def get_order(request, order_id: int):
    """Get details of a specific order."""
    query = {'id': order_id}
    if request.user.is_authenticated:
        query['user'] = request.user
    
    order = get_object_or_404(Order.objects.prefetch_related('items'), **query)
    return order 