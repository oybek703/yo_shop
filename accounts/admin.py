from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account


class AccountAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email',
                    'last_login', 'date_joined', 'is_active')
    list_display_links = ('username', 'first_name',)
    readonly_fields = ('date_joined', 'last_login')
    ordering = ('-date_joined',)

    # As we using custom user model we need to add these
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Account, AccountAdmin)
