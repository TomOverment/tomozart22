from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path("", views.store_home, name="home"),

    path("shop/", views.shop, name="shop"),
    path("cart/", views.cart, name="cart"),

    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/remove/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path("cart/set/<int:product_id>/", views.cart_set_qty, name="cart_set_qty"),
]
