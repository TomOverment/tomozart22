from django.contrib import admin, messages
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse

from .models import Category, Customer, Product, ProductSize, Order, OrderItem
from blog_app.models import MailingListSubscriber


def _abs_url(path: str) -> str:
    base = getattr(settings, "SITE_URL", "http://127.0.0.1:8000").rstrip("/")
    if not path.startswith("/"):
        path = "/" + path
    return base + path


@admin.action(description="Send product drop email to mailing list")
def send_product_drop(modeladmin, request, queryset):
    subs_qs = (
        MailingListSubscriber.objects
        .filter(is_active=True)
        .exclude(email__isnull=True)
        .exclude(email__exact="")
    )

    if not subs_qs.exists():
        messages.warning(request, "No active newsletter subscribers.")
        return

    bcc_list = list(subs_qs.values_list("email", flat=True))

    for product in queryset:
        try:
            product_path = product.get_absolute_url()
        except Exception:
            product_path = reverse("store:product_detail", args=[product.id])

        product_url = _abs_url(product_path)

        image_url = ""
        if getattr(product, "image", None):
            try:
                image_url = product.image.url
                if image_url.startswith("/"):
                    image_url = _abs_url(image_url)
            except Exception:
                image_url = ""

        subject = f"New in the Shop: {product.name}"
        ctx = {
            "product": product,
            "product_url": product_url,
            "image_url": image_url,
        }

        html = render_to_string("emails/product_drop.html", ctx)
        text = render_to_string("emails/product_drop.txt", ctx)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.DEFAULT_FROM_EMAIL],
            bcc=bcc_list,
        )
        msg.attach_alternative(html, "text/html")
        msg.send(fail_silently=False)

    messages.success(
        request,
        f"Sent {queryset.count()} product announcement(s) to {subs_qs.count()} subscriber(s)."
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone")
    search_fields = ("name", "email", "phone")


class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 2
    fields = (
        "name",
        "dimensions_label",
        "width_cm",
        "height_cm",
        "price",
        "stock",
        "edition_total",
        "edition_sold",
        "is_active",
        "sort_order",
    )
    ordering = ("sort_order", "id")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "is_active", "created_at")
    list_filter = ("is_active", "category", "created_at")
    search_fields = ("name", "description")
    actions = [send_product_drop]
    inlines = []


@admin.register(ProductSize)
class ProductSizeAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "display_name",
        "price",
        "stock",
        "edition_total",
        "edition_sold",
        "is_active",
        "sort_order",
    )
    list_filter = ("is_active", "product__category")
    search_fields = ("product__name", "name", "dimensions_label")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        "product",
        "product_size",
        "name",
        "option_name",
        "option_dimensions",
        "unit_price",
        "quantity",
        "line_total",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "email",
        "status",
        "subtotal",
        "shipping_amount",
        "total",
        "created_at",
    )
    list_filter = (
        "status",
        "created_at",
        "shipping_country",
        "billing_country",
    )
    search_fields = (
        "id",
        "full_name",
        "email",
        "stripe_checkout_session_id",
        "stripe_payment_intent_id",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "stripe_checkout_session_id",
        "stripe_payment_intent_id",
        "billing_address_display",
        "shipping_address_display",
    )
    inlines = [OrderItemInline]

    fieldsets = (
        ("Order Status", {
            "fields": (
                "status",
                "created_at",
                "updated_at",
            )
        }),
        ("Customer", {
            "fields": (
                "user",
                "customer",
                "full_name",
                "email",
                "phone",
            )
        }),
        ("Billing Address", {
            "fields": (
                "billing_line1",
                "billing_line2",
                "billing_city",
                "billing_postcode",
                "billing_country",
                "billing_address_display",
            )
        }),
        ("Shipping Address", {
            "fields": (
                "shipping_line1",
                "shipping_line2",
                "shipping_city",
                "shipping_postcode",
                "shipping_country",
                "shipping_address_display",
            )
        }),
        ("Totals", {
            "fields": (
                "currency",
                "subtotal",
                "shipping_amount",
                "total",
            )
        }),
        ("Stripe", {
            "fields": (
                "stripe_checkout_session_id",
                "stripe_payment_intent_id",
            )
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "name",
        "option_name",
        "option_dimensions",
        "unit_price",
        "quantity",
        "line_total",
    )
    search_fields = ("name", "option_name", "option_dimensions", "order__id")
    list_filter = ("order__created_at",)