from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Payment


class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'phone', 'city', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Личная информация', {'fields': ('first_name', 'last_name', 'phone', 'city', 'avatar')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'phone', 'city', 'avatar'),
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'payment_date', 'amount', 'payment_method', 'course', 'lesson')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('user__email', 'course__name', 'lesson__name')
    readonly_fields = ('payment_date',)


admin.site.register(User, CustomUserAdmin)