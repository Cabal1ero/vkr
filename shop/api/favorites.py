from ninja import Router, Schema
from typing import List
from django.shortcuts import get_object_or_404
from shop.models import Favorite, Product
from .schemas import ProductListSchema, ProductImageSchema

router = Router()

class FavoriteActionSchema(Schema):
    product_id: int

def get_session_key(request):
    """Ensures a session key exists."""
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    return session_key

def get_favorites_queryset(request):
    """Returns a queryset of Favorite objects for the current user or session."""
    if request.user.is_authenticated:
        return Favorite.objects.filter(user=request.user)
    else:
        return Favorite.objects.filter(session_key=get_session_key(request))

@router.get("", response=List[ProductListSchema])
def get_favorites(request):
    """Get the list of favorite products."""
    favorites_qs = get_favorites_queryset(request)
    product_ids = favorites_qs.values_list('product_id', flat=True)
    products = Product.objects.filter(id__in=product_ids).prefetch_related('images')
    
    # Manually construct the response to include the main image
    response_data = []
    for product in products:
        main_image = product.images.filter(is_main=True).first()
        response_data.append(
            ProductListSchema(
                id=product.id,
                name=product.name,
                price=product.price,
                original_price=product.original_price,
                rating=product.rating,
                reviews_count=product.reviews_count,
                in_stock=product.in_stock,
                main_image=ProductImageSchema.from_orm(main_image) if main_image else None
            )
        )
    return response_data

@router.post("/add", response={200: dict})
def add_to_favorites(request, payload: FavoriteActionSchema):
    """Add a product to favorites."""
    product = get_object_or_404(Product, id=payload.product_id)
    
    if request.user.is_authenticated:
        favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)
    else:
        session_key = get_session_key(request)
        favorite, created = Favorite.objects.get_or_create(session_key=session_key, product=product)

    if created:
        return {"message": "Product added to favorites."}
    else:
        return {"message": "Product already in favorites."}

@router.delete("/remove", response={200: dict})
def remove_from_favorites(request, payload: FavoriteActionSchema):
    """Remove a product from favorites."""
    product = get_object_or_404(Product, id=payload.product_id)
    
    if request.user.is_authenticated:
        deleted_count, _ = Favorite.objects.filter(user=request.user, product=product).delete()
    else:
        session_key = get_session_key(request)
        deleted_count, _ = Favorite.objects.filter(session_key=session_key, product=product).delete()
        
    if deleted_count > 0:
        return {"message": "Product removed from favorites."}
    else:
        return {"message": "Product not found in favorites."} 