from ninja import Router
from typing import List
from django.shortcuts import get_object_or_404

from shop.models import Product, Category, ProductImage
from .schemas import ProductDetailSchema, ProductListSchema, CategorySchema, ProductImageSchema

router = Router()

@router.get("/categories", response=List[CategorySchema])
def list_categories(request):
    return Category.objects.all()

@router.get("/products", response=List[ProductListSchema])
def list_products(request):
    products = Product.objects.all().prefetch_related('images')
    
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

@router.get("/products/{product_id}", response=ProductDetailSchema)
def get_product(request, product_id: int):
    product = get_object_or_404(
        Product.objects.select_related('category').prefetch_related('images'), 
        id=product_id
    )
    return product

@router.get("/categories/{slug}/products", response=List[ProductListSchema])
def list_products_by_category(request, slug: str):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category).prefetch_related('images')

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