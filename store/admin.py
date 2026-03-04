from django.contrib import admin, messages
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse

from .models import Category, Customer, Product, Order, OrderItem
from blog_app.models import MailingListSubscriber


# Register everything EXCEPT Product here (Product is registered via @admin.register below)
admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderItem)


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
        # Product detail URL
        try:
            product_path = product.get_absolute_url()
        except Exception:
            product_path = reverse("store:product_detail", args=[product.id])

        product_url = _abs_url(product_path)

        # Image URL (best effort)
        image_url = ""
        if getattr(product, "image", None):
            try:
                image_url = product.image.url
                if image_url.startswith("/"):
                    image_url = _abs_url(image_url)
            except Exception:
                image_url = ""

        subject = f"New in the Shop: {product.name}"
        ctx = {"product": product, "product_url": product_url, "image_url": image_url}

        html = render_to_string("emails/product_drop.html", ctx)
        text = render_to_string("emails/product_drop.txt", ctx)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.DEFAULT_FROM_EMAIL],  # keeps Outlook happy
            bcc=bcc_list,
        )
        msg.attach_alternative(html, "text/html")
        msg.send(fail_silently=False)

    messages.success(
        request,
        f"Sent {queryset.count()} product announcement(s) to {subs_qs.count()} subscriber(s)."
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    actions = [send_product_drop]