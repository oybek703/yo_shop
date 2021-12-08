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

    class Meta:
        ordering = ['id']

    def get_url(self):
        return reverse('product_details', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.name


variation_category_choices = (
    ('color', 'color'),
    ('size', 'size')
)


class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(category='color', is_active=True)

    def sizes(self):
        return super(VariationManager, self).filter(category='size', is_active=True)


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations')
    category = models.CharField(max_length=32, choices=variation_category_choices)
    value = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        return self.value
