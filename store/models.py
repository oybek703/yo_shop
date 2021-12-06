from django.db import models
from category.models import Category
from django.urls import reverse


class Product(models.Model):
    name = models.CharField(max_length=64, unique=True)
    slug = models.CharField(max_length=128, unique=True)
    description = models.TextField(max_length=256, blank=True)
    price = models.IntegerField()
    image = models.ImageField(upload_to='images/product')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('product_details', args=[self.category.slug, self.slug])
    def __str__(self):
        return self.name
