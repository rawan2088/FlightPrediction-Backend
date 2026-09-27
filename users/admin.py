from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, Airline


@admin.register(Airline)
class AirlineAdmin(admin.ModelAdmin):
    list_display = ('name', 'iata_code', 'created_at')
    search_fields = ('name', 'iata_code')


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    # Extend Django's built-in UserAdmin rather than admin.ModelAdmin so we
    # keep password hashing, permission widgets, etc. for free — this is
    # also where you, as superuser, promote an account to AIRLINE_STAFF/
    # AIRLINE_ADMIN and set its airline. Never expose that via public API.
    list_display = ('username', 'email', 'role', 'airline', 'is_staff')
    list_filter = ('role', 'airline', 'is_staff', 'is_superuser')
    fieldsets = DjangoUserAdmin.fieldsets + (
        ('Role & Airline', {'fields': ('role', 'airline')}),
    )