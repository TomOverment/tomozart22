from decimal import Decimal

import stripe

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from .models import Product, ProductSize, Order, OrderItem


# -----------------------------
# CART (session-based)
# -----------------------------
CART_SESSION_KEY = "cart"  # e.g. { "12:5": 2, "9:base": 1 }


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

    items = []
    total = Decimal("0.00")

    for cart_key, qty in cart.items():
        qty = int(qty)

        # Base product fallback (no bespoke print options yet)
        if cart_key.endswith(":base"):
            try:
                product_id = int(cart_key.split(":")[0])
            except (ValueError, AttributeError):
                continue

            product = Product.objects.filter(id=product_id, is_active=True).first()
            if not product:
                continue

            unit_price = Decimal(product.price)
            line_total = unit_price * qty
            total += line_total

            items.append({
                "product": product,
                "size": None,
                "qty": qty,
                "unit_price": unit_price,
                "line_total": line_total,
                "cart_key": cart_key,
            })
            continue

        # Bespoke print option
        try:
            product_id_str, size_id_str = cart_key.split(":")
            product_id = int(product_id_str)
            size_id = int(size_id_str)
        except (ValueError, AttributeError):
            continue

        product = Product.objects.filter(id=product_id, is_active=True).first()
        size = ProductSize.objects.filter(
            id=size_id,
            product_id=product_id,
            is_active=True,
        ).first()

        if not product or not size:
            continue

        unit_price = Decimal(size.price)
        line_total = unit_price * qty
        total += line_total

        items.append({
            "product": product,
            "size": size,
            "qty": qty,
            "unit_price": unit_price,
            "line_total": line_total,
            "cart_key": cart_key,
        })

    return render(request, "store/cart.html", {
        "items": items,
        "total": total,
        "count": sum(int(q) for q in cart.values()),
    })




def cart_add(request, product_id):
    if request.method != "POST":
        return redirect("store:product_detail", product_id=product_id)

    cart = _get_cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)

    active_sizes = product.sizes.filter(is_active=True)
    size_id = request.POST.get("size_id")

    # Product has bespoke print options
    if active_sizes.exists():
        if not size_id:
            messages.warning(request, "Please select a print option.")
            return redirect("store:product_detail", product_id=product_id)

        size = get_object_or_404(
            ProductSize,
            id=size_id,
            product=product,
            is_active=True,
        )

        cart_key = f"{product.id}:{size.id}"
        cart[cart_key] = int(cart.get(cart_key, 0)) + 1
        request.session.modified = True

        cart_count = sum(int(q) for q in cart.values())

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({
                "success": True,
                "cart_count": cart_count,
            })

        messages.success(request, f"Added {product.name} ({size.display_name}) to cart.")
        return redirect("store:cart")

    # Product has no bespoke print options yet
    cart_key = f"{product.id}:base"
    cart[cart_key] = int(cart.get(cart_key, 0)) + 1
    request.session.modified = True

    cart_count = sum(int(q) for q in cart.values())

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "cart_count": cart_count,
        })

    messages.success(request, f"Added {product.name} to cart.")
    return redirect("store:cart")

def cart_remove(request):
    cart = _get_cart(request)
    cart_key = request.POST.get("cart_key")

    if cart_key in cart:
        del cart[cart_key]
        request.session.modified = True
        messages.info(request, "Removed from cart.")

    return redirect("store:cart")


def cart_set_qty(request):
    cart = _get_cart(request)
    cart_key = request.POST.get("cart_key")

    try:
        qty = int(request.POST.get("qty", "1"))
    except ValueError:
        qty = 1

    qty = max(0, min(qty, 99))

    if cart_key in cart:
        if qty == 0:
            cart.pop(cart_key, None)
        else:
            cart[cart_key] = qty
        request.session.modified = True

    return redirect("store:cart")


def cart_inc(request):
    cart = _get_cart(request)
    cart_key = request.POST.get("cart_key")

    if cart_key in cart:
        cart[cart_key] = int(cart.get(cart_key, 0)) + 1
        request.session.modified = True

    return redirect("store:cart")


def cart_dec(request):
    cart = _get_cart(request)
    cart_key = request.POST.get("cart_key")

    if cart_key in cart:
        current = int(cart.get(cart_key, 0))
        if current <= 1:
            cart.pop(cart_key, None)
        else:
            cart[cart_key] = current - 1
        request.session.modified = True

    return redirect("store:cart")


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    sizes = product.sizes.filter(is_active=True).order_by("sort_order", "id")

    return render(request, "store/product_detail.html", {
        "product": product,
        "sizes": sizes,
    })


# -----------------------------
# STRIPE
# -----------------------------
stripe.api_key = settings.STRIPE_SECRET_KEY


# -----------------------------
# SHIPPING HELPERS
# -----------------------------
def _build_shipping_options():
    return [
        {
            "shipping_rate_data": {
                "type": "fixed_amount",
                "fixed_amount": {
                    "amount": 495,
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
                    "amount": 1495,
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
    return [
        "GB",
        "IE",
        "FR",
        "DE",
        "ES",
        "IT",
        "NL",
        "BE",
        "PT",
        "SE",
        "DK",
        "NO",
        "CH",
        "AT",
        "PL",
        "US",
        "CA",
        "AU",
        "NZ",
    ]


# -----------------------------
# CHECKOUT (Stripe Checkout)
# -----------------------------
def checkout_start(request):
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

    for cart_key, qty in cart.items():
        qty = int(qty)

        # Base product fallback
        if cart_key.endswith(":base"):
            try:
                product_id = int(cart_key.split(":")[0])
            except (ValueError, AttributeError):
                continue

            product = Product.objects.filter(id=product_id, is_active=True).first()
            if not product:
                continue

            unit_price = Decimal(product.price)
            subtotal += unit_price * qty

            OrderItem.objects.create(
                order=order,
                product=product,
                name=product.name,
                option_name="",
                option_dimensions="",
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
            continue

        # Bespoke print option
        try:
            product_id_str, size_id_str = cart_key.split(":")
            product_id = int(product_id_str)
            size_id = int(size_id_str)
        except (ValueError, AttributeError):
            continue

        product = Product.objects.filter(id=product_id, is_active=True).first()
        size = ProductSize.objects.filter(
            id=size_id,
            product_id=product_id,
            is_active=True,
        ).first()

        if not product or not size:
            continue

        unit_price = Decimal(size.price)
        subtotal += unit_price * qty

        OrderItem.objects.create(
            order=order,
            product=product,
            product_size=size,
            name=product.name,
            option_name=size.name or size.display_name,
            option_dimensions=size.dimensions_label,
            unit_price=unit_price,
            quantity=qty,
        )

        item_name = f"{product.name} - {size.display_name}"

        line_items.append({
            "price_data": {
                "currency": "gbp",
                "product_data": {
                    "name": item_name,
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
            metadata={"order_id": str(order.id)},
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
    session_id = request.GET.get("session_id")
    order = None

    if session_id:
        order = Order.objects.filter(
            stripe_checkout_session_id=session_id
        ).first()

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
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )
    except ValueError:
        return HttpResponse("Invalid payload", status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse("Invalid signature", status=400)
    except Exception as e:
        return HttpResponse(f"Webhook error: {e}", status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        order_id = (session.get("metadata") or {}).get("order_id")
        payment_intent = session.get("payment_intent")

        if order_id:
            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                return HttpResponse(status=200)

            if order.status != Order.Status.PAID:
                order.status = Order.Status.PAID
                order.stripe_payment_intent_id = payment_intent or ""

                customer_details = session.get("customer_details") or {}
                shipping_details = session.get("shipping_details") or {}
                shipping_cost = session.get("shipping_cost") or {}

                order.email = customer_details.get("email") or order.email
                order.phone = customer_details.get("phone") or order.phone
                order.full_name = (
                    shipping_details.get("name")
                    or customer_details.get("name")
                    or order.full_name
                )

                address = shipping_details.get("address") or {}

                order.shipping_line1 = address.get("line1", "")
                order.shipping_line2 = address.get("line2", "")
                order.shipping_city = address.get("city", "")
                order.shipping_postcode = address.get("postal_code", "")
                order.shipping_country = address.get("country", "")

                billing_address = (customer_details.get("address") or {})
                order.billing_line1 = billing_address.get("line1", "")
                order.billing_line2 = billing_address.get("line2", "")
                order.billing_city = billing_address.get("city", "")
                order.billing_postcode = billing_address.get("postal_code", "")
                order.billing_country = billing_address.get("country", "")

                order.save()

                order_items = order.items.all()
                items_text = "\n".join(
                    [
                        (
                            f"- {item.quantity} x {item.name}"
                            f"{f' ({item.option_name})' if item.option_name else ''}"
                            f"{f' — {item.option_dimensions}' if item.option_dimensions else ''}"
                            f" (£{item.unit_price} each)"
                        )
                        for item in order_items
                    ]
                )

                shipping_address = order.shipping_address_display or "Not provided"
                billing_address = order.billing_address_display or "Not provided"

                shipping_amount = shipping_cost.get("amount_total")
                if shipping_amount is not None:
                    order.shipping_amount = Decimal(shipping_amount) / Decimal("100")

                amount_total = session.get("amount_total")
                if amount_total is not None:
                    order.total = Decimal(amount_total) / Decimal("100")

                order.save()

                if order.email:
                    customer_subject = f"Tomozart order confirmation #{order.id}"
                    customer_message = (
                        f"Hi {order.full_name or 'there'},\n\n"
                        f"Thank you for your order from Tomozart.\n\n"
                        f"Order number: {order.id}\n"
                        f"Payment status: Paid\n\n"
                        f"Items:\n{items_text}\n\n"
                        f"Subtotal: £{order.subtotal}\n"
                        f"Shipping: £{order.shipping_amount}\n"
                        f"Total: £{order.total}\n\n"
                        f"Shipping address:\n{shipping_address}\n\n"
                        f"Billing address:\n{billing_address}\n\n"
                        f"If you have any questions, reply to this email.\n\n"
                        f"Tomozart"
                    )

                    send_mail(
                        subject=customer_subject,
                        message=customer_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[order.email],
                        fail_silently=False,
                    )

                if settings.ADMIN_EMAIL:
                    admin_subject = f"New paid Tomozart order #{order.id}"
                    admin_message = (
                        f"A new order has been paid.\n\n"
                        f"Order number: {order.id}\n"
                        f"Customer: {order.full_name or 'Unknown'}\n"
                        f"Email: {order.email or 'Unknown'}\n\n"
                        f"Items:\n{items_text}\n\n"
                        f"Subtotal: £{order.subtotal}\n"
                        f"Shipping: £{order.shipping_amount}\n"
                        f"Total: £{order.total}\n\n"
                        f"Shipping address:\n{shipping_address}\n\n"
                        f"Billing address:\n{billing_address}\n"
                    )

                    send_mail(
                        subject=admin_subject,
                        message=admin_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[settings.ADMIN_EMAIL],
                        fail_silently=False,
                    )

    elif event["type"] == "payment_intent.payment_failed":
        payment_intent = event["data"]["object"]
        payment_intent_id = payment_intent.get("id")

        if payment_intent_id:
            Order.objects.filter(
                stripe_payment_intent_id=payment_intent_id
            ).update(status=Order.Status.FAILED)

    return HttpResponse(status=200)