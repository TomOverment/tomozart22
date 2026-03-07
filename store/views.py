from decimal import Decimal

import stripe

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
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

    cart_count = sum(int(q) for q in cart.values())

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"cart_count": cart_count})

    messages.success(request, "Added to cart.")
    return redirect(request.META.get("HTTP_REFERER", reverse("store:shop")))


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
        cart.pop(pid, None)
    else:
        cart[pid] = current - 1

    request.session.modified = True
    return redirect("store:cart")


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, "store/product_detail.html", {"product": product})


# -----------------------------
# STRIPE
# -----------------------------
stripe.api_key = settings.STRIPE_SECRET_KEY


# -----------------------------
# SHIPPING HELPERS
# -----------------------------
def _build_shipping_options():
    """
    Stripe shipping options.
    Amounts are in pence because currency is GBP.
    Edit these values/names as needed.
    """
    return [
        {
            "shipping_rate_data": {
                "type": "fixed_amount",
                "fixed_amount": {
                    "amount": 495,  # £4.95
                    "currency": "gbp",
                },
                "display_name": "UK Standard Shipping",
                "delivery_estimate": {
                    "minimum": {"unit": "business_day", "value": 2},
                    "maximum": {"unit": "business_day", "value": 5},
                },
            }
        },
        {
            "shipping_rate_data": {
                "type": "fixed_amount",
                "fixed_amount": {
                    "amount": 1495,  # £14.95
                    "currency": "gbp",
                },
                "display_name": "International Shipping",
                "delivery_estimate": {
                    "minimum": {"unit": "business_day", "value": 5},
                    "maximum": {"unit": "business_day", "value": 12},
                },
            }
        },
    ]


def _allowed_shipping_countries():
    """
    Add/remove countries as needed.
    Stripe expects ISO country codes.
    """
    return [
        "GB",  # United Kingdom
        "IE",  # Ireland
        "FR",  # France
        "DE",  # Germany
        "ES",  # Spain
        "IT",  # Italy
        "NL",  # Netherlands
        "BE",  # Belgium
        "PT",  # Portugal
        "SE",  # Sweden
        "DK",  # Denmark
        "NO",  # Norway
        "CH",  # Switzerland
        "AT",  # Austria
        "PL",  # Poland
        "US",  # United States
        "CA",  # Canada
        "AU",  # Australia
        "NZ",  # New Zealand
    ]


# -----------------------------
# CHECKOUT (Stripe Checkout)
# -----------------------------
def checkout_start(request):
    """
    Creates a pending Order + OrderItems from the session cart,
    then creates a Stripe Checkout Session and redirects the user.
    """
    cart = _get_cart(request)
    if not cart:
        messages.warning(request, "Your cart is empty.")
        return redirect("store:cart")

    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        email=(getattr(request.user, "email", "") or "") if request.user.is_authenticated else "",
        status=Order.Status.PENDING,
        currency="gbp",
    )

    line_items = []
    subtotal = Decimal("0.00")

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

        line_items.append({
            "price_data": {
                "currency": "gbp",
                "product_data": {
                    "name": product.name,
                },
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
    order.total = subtotal
    order.save(update_fields=["subtotal", "total"])

    success_url = request.build_absolute_uri(
        reverse("store:checkout_success")
    ) + "?session_id={CHECKOUT_SESSION_ID}"

    cancel_url = request.build_absolute_uri(
        reverse("store:checkout_cancel")
    ) + f"?order_id={order.id}"

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=line_items,
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "order_id": str(order.id),
            },
            client_reference_id=str(order.id),
            customer_email=order.email or None,
            billing_address_collection="required",
            phone_number_collection={"enabled": True},
            shipping_address_collection={
                "allowed_countries": _allowed_shipping_countries(),
            },
            shipping_options=_build_shipping_options(),
            customer_creation="always",
        )
    except Exception:
        order.status = Order.Status.CANCELED
        order.save(update_fields=["status"])
        messages.error(request, "Unable to start checkout. Please try again.")
        return redirect("store:cart")

    order.stripe_checkout_session_id = session.id
    order.save(update_fields=["stripe_checkout_session_id"])

    return redirect(session.url, permanent=False)


def checkout_success(request):
    """
    User returns from Stripe.
    Webhook is the source of truth for marking the order as paid.
    """
    session_id = request.GET.get("session_id")
    order = None

    if session_id:
        order = Order.objects.filter(
            stripe_checkout_session_id=session_id
        ).first()

    # Only clear cart if the order is confirmed as paid
    if order and order.status == Order.Status.PAID:
        request.session[CART_SESSION_KEY] = {}
        request.session.modified = True

    return render(request, "store/checkout_success.html", {"order": order})


def checkout_cancel(request):
    order_id = request.GET.get("order_id")
    if order_id:
        Order.objects.filter(
            id=order_id,
            status=Order.Status.PENDING
        ).update(status=Order.Status.CANCELED)

    messages.info(request, "Checkout canceled.")
    return redirect("store:cart")


# -----------------------------
# WEBHOOK
# -----------------------------
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
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    except Exception:
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        metadata = session.get("metadata") or {}
        order_id = metadata.get("order_id") or session.get("client_reference_id")
        payment_intent = session.get("payment_intent")

        if order_id:
            order = Order.objects.filter(id=order_id).first()

            if order:
                customer_details = session.get("customer_details") or {}
                shipping_details = session.get("shipping_details") or {}

                # Stripe may include shipping cost separately
                amount_total = session.get("amount_total")
                shipping_cost_data = session.get("shipping_cost") or {}
                shipping_amount = shipping_cost_data.get("amount_total")

                billing_address = customer_details.get("address") or {}
                shipping_address = shipping_details.get("address") or {}

                order.status = Order.Status.PAID
                order.stripe_payment_intent_id = payment_intent or ""
                order.email = customer_details.get("email") or order.email

                # If these fields exist on your model, save them
                if hasattr(order, "full_name"):
                    order.full_name = (
                        shipping_details.get("name")
                        or customer_details.get("name")
                        or ""
                    )

                if hasattr(order, "phone"):
                    order.phone = customer_details.get("phone") or ""

                if hasattr(order, "shipping_line1"):
                    order.shipping_line1 = shipping_address.get("line1", "")
                    order.shipping_line2 = shipping_address.get("line2", "")
                    order.shipping_city = shipping_address.get("city", "")
                    order.shipping_postcode = shipping_address.get("postal_code", "")
                    order.shipping_country = shipping_address.get("country", "")

                if hasattr(order, "billing_line1"):
                    order.billing_line1 = billing_address.get("line1", "")
                    order.billing_line2 = billing_address.get("line2", "")
                    order.billing_city = billing_address.get("city", "")
                    order.billing_postcode = billing_address.get("postal_code", "")
                    order.billing_country = billing_address.get("country", "")

                if hasattr(order, "shipping_amount") and shipping_amount is not None:
                    order.shipping_amount = Decimal(shipping_amount) / Decimal("100")

                if amount_total is not None:
                    order.total = Decimal(amount_total) / Decimal("100")

                order.save()

    elif event["type"] == "payment_intent.payment_failed":
        payment_intent = event["data"]["object"]
        payment_intent_id = payment_intent.get("id")

        if payment_intent_id:
            Order.objects.filter(
                stripe_payment_intent_id=payment_intent_id
            ).update(status=Order.Status.CANCELED)

    return HttpResponse(status=200)