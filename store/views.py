from decimal import Decimal
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Product

CART_SESSION_KEY = "cart"  # { "12": 2, "9": 1 }

def _get_cart(request):
    cart = request.session.get(CART_SESSION_KEY)
    if cart is None:
        cart = {}
        request.session[CART_SESSION_KEY] = cart
    return cart

def store_home(request):
    return redirect("store:shop")

def shop(request):
    products = Product.objects.all().order_by("name")
    return render(request, "store/shop.html", {"products": products})

def cart(request):
    cart = _get_cart(request)

    product_ids = [int(pid) for pid in cart.keys()]
    products = Product.objects.filter(id__in=product_ids)

    items = []
    total = Decimal("0.00")

    for p in products:
        qty = int(cart.get(str(p.id), 0))
        line_total = (p.price or Decimal("0.00")) * qty
        total += line_total
        items.append({
            "product": p,
            "qty": qty,
            "line_total": line_total,
        })

    return render(request, "store/cart.html", {
        "items": items,
        "total": total,
        "count": sum(int(q) for q in cart.values()),
    })

def cart_add(request, product_id):
    cart = _get_cart(request)
    pid = str(product_id)
    cart[pid] = int(cart.get(pid, 0)) + 1
    request.session.modified = True
    messages.success(request, "Added to cart.")
    return redirect(request.META.get("HTTP_REFERER", "store:shop"))

def cart_remove(request, product_id):
    cart = _get_cart(request)
    pid = str(product_id)
    if pid in cart:
        del cart[pid]
        request.session.modified = True
        messages.info(request, "Removed from cart.")
    return redirect("store:cart")

def cart_set_qty(request, product_id):
    cart = _get_cart(request)
    pid = str(product_id)

    try:
        qty = int(request.POST.get("qty", "1"))
    except ValueError:
        qty = 1

    qty = max(0, min(qty, 99))

    if qty == 0:
        cart.pop(pid, None)
    else:
        cart[pid] = qty

    request.session.modified = True
    return redirect("store:cart")
