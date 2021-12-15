from django.db import models
from accounts.models import Account
from store.models import Product, Variation


class Payment(models.Model):
    payment_id = models.CharField(max_length=128)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=256)
    paid_amount = models.CharField(max_length=128)
    status = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)


class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    order_number = models.CharField(max_length=32)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    phone_number = models.CharField(max_length=16)
    email = models.EmailField(max_length=64)
    address_line_1 = models.CharField(max_length=64)
    address_line_2 = models.CharField(max_length=16, blank=True)
    country = models.CharField(max_length=32)
    state = models.CharField(max_length=16)
    city = models.CharField(max_length=32)
    order_note = models.TextField(max_length=16, blank=True)
    total = models.FloatField()
    tax = models.FloatField()
    status = models.CharField(max_length=64, choices=STATUS, default='New')
    ip = models.CharField(max_length=32, blank=True)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'

    def __str__(self):
        return self.first_name


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    product_quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_cost(self):
        return round(self.product_price * self.product_quantity, 2)

    def __str__(self):
        return self.product.name












