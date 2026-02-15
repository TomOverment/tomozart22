from decimal import Decimal

import stripe

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import Product, Order, OrderItem


# -----------------------------
# CART (session-based)
# -----------------------------
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
    products = Product.objects.filter(is_active=True).order_by("name")
    return render(request, "store/shop.html", {"products": products})


def cart(request):
    cart = _get_cart(request)

    product_ids = [int(pid) for pid in cart.keys()] if cart else []
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


# -----------------------------
# CHECKOUT (Stripe Checkout)
# -----------------------------
stripe.api_key = settings.STRIPE_SECRET_KEY


def checkout_start(request):
    """
    Creates a pending Order + OrderItems from the session cart,
    then creates a Stripe Checkout Session and redirects the user.
    """
    cart = _get_cart(request)
    if not cart:
        messages.warning(request, "Your cart is empty.")
        return redirect("store:cart")

    # Create pending order
    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        email=(getattr(request.user, "email", "") or "") if request.user.is_authenticated else "",
        status=Order.Status.PENDING,
        currency="gbp",
    )

    line_items = []
    subtotal = Decimal("0.00")

    # Build order items from cart
    product_ids = [int(pid) for pid in cart.keys()]
    products = Product.objects.filter(id__in=product_ids)

    product_by_id = {p.id: p for p in products}

    for pid_str, qty in cart.items():
        pid = int(pid_str)
        qty = int(qty)

        product = product_by_id.get(pid)
        if not product:
            continue

        unit_price = Decimal(str(product.price or Decimal("0.00")))
        subtotal += unit_price * qty

        OrderItem.objects.create(
            order=order,
            product=product,
            name=product.name,
            unit_price=unit_price,
            quantity=qty,
        )

        # Stripe uses smallest currency unit (pence)
        line_items.append({
            "price_data": {
                "currency": "gbp",
                "product_data": {"name": product.name},
                "unit_amount": int((unit_price * 100).quantize(Decimal("1"))),
            },
            "quantity": qty,
        })

    if not line_items:
        order.status = Order.Status.CANCELED
        order.save(update_fields=["status"])
        messages.warning(request, "Your cart contained no valid products.")
        return redirect("store:cart")

    order.subtotal = subtotal
    order.total = subtotal  # extend later with shipping/tax if needed
    order.save(update_fields=["subtotal", "total"])

    success_url = request.build_absolute_uri(
        reverse("store:checkout_success")
    ) + f"?order_id={order.id}"

    cancel_url = request.build_absolute_uri(
        reverse("store:checkout_cancel")
    ) + f"?order_id={order.id}"

    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=line_items,
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"order_id": str(order.id)},
        customer_email=order.email or None,
    )

    order.stripe_checkout_session_id = session.id
    order.save(update_fields=["stripe_checkout_session_id"])

    return redirect(session.url, permanent=False)


def checkout_success(request):
    """
    User returns from Stripe. Do NOT mark paid here.
    Webhook is the source of truth.
    """
    order_id = request.GET.get("order_id")
    order = get_object_or_404(Order, id=order_id)

    # Optional: clear cart now (some prefer clearing only after webhook)
    request.session[CART_SESSION_KEY] = {}
    request.session.modified = True

    return render(request, "store/checkout_success.html", {"order": order})


def checkout_cancel(request):
    order_id = request.GET.get("order_id")
    if order_id:
        Order.objects.filter(id=order_id, status=Order.Status.PENDING).update(
            status=Order.Status.CANCELED
        )
    messages.info(request, "Checkout canceled.")
    return redirect("store:cart")

def cart_inc(request, product_id):
    cart = _get_cart(request)
    pid = str(product_id)
    cart[pid] = int(cart.get(pid, 0)) + 1
    request.session.modified = True
    return redirect("store:cart")


def cart_dec(request, product_id):
    cart = _get_cart(request)
    pid = str(product_id)
    current = int(cart.get(pid, 0))

    if current <= 1:
        cart.pop(pid, None)   # remove item
    else:
        cart[pid] = current - 1

    request.session.modified = True
    return redirect("store:cart")


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, "store/product_detail.html", {"product": product})



@csrf_exempt
def stripe_webhook(request):
    """
    Stripe calls this endpoint. It confirms payment and updates the Order.
    """
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )
    except Exception:
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        order_id = (session.get("metadata") or {}).get("order_id")
        payment_intent = session.get("payment_intent")

        if order_id:
            Order.objects.filter(id=order_id).update(
                status=Order.Status.PAID,
                stripe_payment_intent_id=payment_intent or "",
            )

    return HttpResponse(status=200)
