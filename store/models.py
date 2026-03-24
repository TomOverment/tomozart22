from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.urls import reverse
from django.utils import timezone


# -----------------------------
# CATALOG
# -----------------------------
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Customer(models.Model):
    """
    Optional customer profile table.
    Useful for guest checkout or linking extra data to a Django user later.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customer_profile",
    )
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    address = models.CharField(max_length=255, default="", blank=True, null=True)
    phone = models.CharField(max_length=20, default="", blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.email})"


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
    )
    image = models.ImageField(upload_to="products/")
    description = models.TextField(max_length=500, default="", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("store:product_detail", args=[self.id])

    @property
    def optimized_image_url(self):
        if not self.image:
            return ""
        return self.image.url.replace("/upload/", "/upload/f_auto,q_auto/")

class ProductSize(models.Model):
    SIZE_CHOICES = [
        ("S", "Small"),
        ("M", "Medium"),
        ("L", "Large"),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="sizes",
    )
    size_code = models.CharField(max_length=1, choices=SIZE_CHOICES)
    label = models.CharField(max_length=100, blank=True, default="")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["size_code"]
        unique_together = ("product", "size_code")

    def __str__(self):
        if self.label:
            return f"{self.product.name} - {self.get_size_code_display()} ({self.label})"
        return f"{self.product.name} - {self.get_size_code_display()}"

# -----------------------------
# ORDERS / CHECKOUT
# -----------------------------
class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        SHIPPED = "shipped", "Shipped"
        CANCELED = "canceled", "Canceled"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    # Who placed the order
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )

    # Optional link to your Customer table
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    # Contact snapshot at time of purchase
    full_name = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)

    # Billing address
    billing_line1 = models.CharField(max_length=255, blank=True)
    billing_line2 = models.CharField(max_length=255, blank=True)
    billing_city = models.CharField(max_length=120, blank=True)
    billing_postcode = models.CharField(max_length=30, blank=True)
    billing_country = models.CharField(max_length=2, blank=True)

    # Shipping address
    shipping_line1 = models.CharField(max_length=255, blank=True)
    shipping_line2 = models.CharField(max_length=255, blank=True)
    shipping_city = models.CharField(max_length=120, blank=True)
    shipping_postcode = models.CharField(max_length=30, blank=True)
    shipping_country = models.CharField(max_length=2, blank=True)

    currency = models.CharField(max_length=10, default="gbp")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    shipping_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    # Stripe references
    stripe_checkout_session_id = models.CharField(max_length=255, blank=True)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        who = self.email or (self.customer.email if self.customer else "guest")
        return f"Order {self.id} ({self.status}) - {who}"

    @property
    def billing_address_display(self):
        parts = [
            self.billing_line1,
            self.billing_line2,
            self.billing_city,
            self.billing_postcode,
            self.billing_country,
        ]
        return ", ".join([part for part in parts if part])

    @property
    def shipping_address_display(self):
        parts = [
            self.shipping_line1,
            self.shipping_line2,
            self.shipping_city,
            self.shipping_postcode,
            self.shipping_country,
        ]
        return ", ".join([part for part in parts if part])

    def recalc_totals(self, save=True):
        subtotal = self.items.aggregate(s=Sum("line_total"))["s"] or Decimal("0.00")
        self.subtotal = Decimal(subtotal).quantize(Decimal("0.01"))
        self.total = (self.subtotal + self.shipping_amount).quantize(Decimal("0.01"))

        if save:
            self.save(update_fields=["subtotal", "total"])

        return self.total


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    product_size = models.ForeignKey(
        "ProductSize",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
    )

    name = models.CharField(max_length=100, blank=True, null=True)
    size_code = models.CharField(max_length=1, blank=True, default="")
    size_label = models.CharField(max_length=100, blank=True, default="")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    line_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    def __str__(self):
        size_part = f" - {self.size_code}" if self.size_code else ""
        return f"{self.quantity} x {self.name}{size_part} (Order {self.order.id})"

    def save(self, *args, **kwargs):
        unit_price = Decimal(self.unit_price or Decimal("0.00"))
        quantity = Decimal(self.quantity or 0)
        self.line_total = (unit_price * quantity).quantize(Decimal("0.01"))
        super().save(*args, **kwargs)