from ninja import Router, Schema
from django.shortcuts import get_object_or_404
from shop.models import Product, CartItem
from shop.utils import get_or_create_cart
from .schemas import CartSchema, CartItemSchema, CartProductSchema

router = Router()

class AddToCartSchema(Schema):
    product_id: int
    quantity: int = 1

class UpdateCartSchema(Schema):
    item_id: int
    quantity: int

class RemoveFromCartSchema(Schema):
    item_id: int

def get_cart_data(cart):
    """Helper to structure cart data for the response."""
    items = cart.items.select_related('product').all()
    total = sum(item.product.price * item.quantity for item in items)
    
    cart_items_data = []
    for item in items:
        main_image = item.product.images.filter(is_main=True).first()
        cart_items_data.append({
            "id": item.id,
            "product": {
                "id": item.product.id,
                "name": item.product.name,
                "price": item.product.price,
                "image": main_image.image.url if main_image else None
            },
            "quantity": item.quantity
        })

    return {"items": cart_items_data, "total": total}


@router.get("", response=CartSchema)
def get_cart(request):
    """Get the current user's or session's cart."""
    cart = get_or_create_cart(request)
    return get_cart_data(cart)

@router.post("/add", response=CartSchema)
def add_to_cart(request, payload: AddToCartSchema):
    """Add a product to the cart."""
    cart = get_or_create_cart(request)
    product = get_object_or_404(Product, id=payload.product_id)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, 
        product=product,
        defaults={'quantity': payload.quantity}
    )
    
    if not created:
        cart_item.quantity += payload.quantity
        cart_item.save()
        
    return get_cart_data(cart)

@router.put("/update", response=CartSchema)
def update_cart_item(request, payload: UpdateCartSchema):
    """Update the quantity of an item in the cart."""
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=payload.item_id, cart=cart)
    
    if payload.quantity > 0:
        item.quantity = payload.quantity
        item.save()
    else:
        item.delete() # Remove item if quantity is 0 or less
        
    return get_cart_data(cart)

@router.delete("/remove", response=CartSchema)
def remove_from_cart(request, payload: RemoveFromCartSchema):
    """Remove an item from the cart."""
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=payload.item_id, cart=cart)
    item.delete()
    return get_cart_data(cart)

@router.delete("/clear", response=CartSchema)
def clear_cart(request):
    """Clear all items from the cart."""
    cart = get_or_create_cart(request)
    cart.items.all().delete()
    return get_cart_data(cart) 