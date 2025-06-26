from ninja import NinjaAPI
from users.api.auth import router as auth_router
from shop.api.products import router as products_router
from shop.api.cart import router as cart_router
from shop.api.favorites import router as favorites_router
from shop.api.orders import router as orders_router
from shop.api.webhooks import router as webhooks_router

api = NinjaAPI(
    title="E-commerce API",
    description="API for an online store.",
    version="1.0.0",
)

api.add_router("/auth", auth_router)
api.add_router("/", products_router)
api.add_router("/cart", cart_router)
api.add_router("/favorites", favorites_router)
api.add_router("/orders", orders_router)
api.add_router("/webhooks", webhooks_router)

# Тут мы будем подключать роутеры из приложений
# from shop.api.products import router as products_router
#
# api.add_router("/products", products_router) 