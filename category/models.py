from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=32)
    slug = models.SlugField(max_length=64, unique=True)
    description = models.TextField(max_length=256, blank=True)
    category_image = models.ImageField(upload_to='images/category', blank=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name
