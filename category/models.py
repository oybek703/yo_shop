from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    category_name = models.CharField(max_length=32)
    description = models.TextField(max_length=256, blank=True)
    slug = models.SlugField()
    category_image = models.ImageField(upload_to='images/category', blank=True)

    def save(self, *args, **kwargs):
        category = self.save(*args, **kwargs)
        category.slug = slugify(self.slug)
        return category

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.category_name
