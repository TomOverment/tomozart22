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
    path("checkout/", views.checkout_start, name="checkout_start"),
    path("checkout/success/", views.checkout_success, name="checkout_success"),
    path("checkout/cancel/", views.checkout_cancel, name="checkout_cancel"),
    path("stripe/webhook/", views.stripe_webhook, name="stripe_webhook"),
    path("cart/inc/<int:product_id>/", views.cart_inc, name="cart_inc"),
    path("cart/dec/<int:product_id>/", views.cart_dec, name="cart_dec"),
    path("product/<int:product_id>/", views.product_detail, name="product_detail"),
    path("stripe/webhook/", views.stripe_webhook, name="stripe_webhook"),

]
