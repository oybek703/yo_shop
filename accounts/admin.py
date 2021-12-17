from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import Account, UserProfile


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


class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        return format_html('<img src={} width="30" style="border-radius:50%;">'.format(object.profile_picture.url))
    thumbnail.short_description = 'Profile Picture'
    list_display = ('thumbnail', 'user', 'city', 'state', 'country')


admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
