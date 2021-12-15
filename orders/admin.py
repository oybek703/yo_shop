from django.contrib import admin

from orders.models import Order, OrderProduct, Payment


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment', 'product', 'product_quantity', 'ordered', 'product_price',
                       'user', 'variations')
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'phone_number', 'email', 'city', 'total', 'tax', 'status',
                    'is_ordered', 'created_at']
    list_filter = ['status', 'is_ordered']
    search_fields = ['order_number', 'first_name', 'last_name','email', 'phone_number']
    list_per_page = 20
    inlines = [OrderProductInline]


admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)
