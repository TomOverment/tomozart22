from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils import timezone


# -----------------------------
# CATALOG
# -----------------------------
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Customer(models.Model):
    """
    Optional customer profile table.
    If you rely on Django/allauth users, you can keep this for guest checkout
    or connect it to User later.
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
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    image = models.ImageField(upload_to="products/")
    description = models.TextField(max_length=500, default="", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

# -----------------------------
# ORDERS / CHECKOUT
# -----------------------------
class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        CANCELED = "canceled", "Canceled"
        FAILED = "failed", "Failed"

    # Who placed the order (optional for guest checkout)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    # Optional link to your Customer table
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True
    )

    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    # Contact / delivery info at time of purchase (keep snapshot here)
    full_name = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=120, blank=True)
    postcode = models.CharField(max_length=30, blank=True)
    country = models.CharField(max_length=2, default="GB")  # ISO code

    currency = models.CharField(max_length=10, default="gbp")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    # Stripe references (for payment confirmation / refunds)
    stripe_checkout_session_id = models.CharField(max_length=255, blank=True)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True)

    def __str__(self):
        who = self.email or (self.customer.email if self.customer else "guest")
        return f"Order {self.id} ({self.status}) - {who}"

    def recalc_totals(self, save=True):
        subtotal = self.items.aggregate(s=models.Sum("line_total"))["s"] or Decimal("0.00")
        self.subtotal = subtotal
        self.total = (self.subtotal + self.shipping).quantize(Decimal("0.01"))
        if save:
            self.save(update_fields=["subtotal", "total"])
        return self.total


class OrderItem(models.Model):
    """
    One row per product purchased.
    Stores snapshot of name + unit_price so historical orders remain correct
    even if product price changes later.
    """
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    name = models.CharField(max_length=100, blank=True, null=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    line_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    def __str__(self):
        return f"{self.quantity} x {self.name} (Order {self.order.id})"

    def save(self, *args, **kwargs):
        self.line_total = (Decimal(self.unit_price) * Decimal(self.quantity)).quantize(Decimal("0.01"))
        super().save(*args, **kwargs)
