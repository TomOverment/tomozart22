from itertools import product
from django.db import models
import datetime

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    address = models.CharField(max_length=255, default='', blank=True, null=True)
    phone = models.CharField(max_length=20, default='', blank=True, null=True)

    def __str__(self):
        return f'{self.name} ({self.email})'

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    image = models.ImageField(upload_to="products/")
    description = models.TextField(max_length=500, default='',blank=True, null=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through="OrderItem")
    date_ordered = models.DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return f"Order {self.id} by {self.customer.name}"

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    email = models.EmailField(default='', blank=True, null=True)
    phone = models.CharField(max_length=20, default='', blank=True, null=True)
    adress = models.CharField(max_length=255, default='', blank=True, null=True)
    date = models.DateTimeField(default=datetime.datetime.now)
    status = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"
