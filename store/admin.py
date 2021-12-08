from django.contrib import admin
from .models import Product, Variation


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'category', 'modified_date', 'is_available')
    prepopulated_fields = {'slug': ('name',)}


class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'value', 'category', 'created_at', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'value', 'category')


admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
