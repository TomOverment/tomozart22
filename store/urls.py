from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path("", views.store_home, name="home"),

    path("shop/", views.shop, name="shop"),
    path("cart/", views.cart, name="cart"),

    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/remove/", views.cart_remove, name="cart_remove"),
    path("cart/set-qty/", views.cart_set_qty, name="cart_set_qty"),
    path("cart/inc/", views.cart_inc, name="cart_inc"),
    path("cart/dec/", views.cart_dec, name="cart_dec"),

    path("checkout/", views.checkout_start, name="checkout_start"),
    path("checkout/success/", views.checkout_success, name="checkout_success"),
    path("checkout/cancel/", views.checkout_cancel, name="checkout_cancel"),

    path("product/<int:product_id>/", views.product_detail, name="product_detail"),
]