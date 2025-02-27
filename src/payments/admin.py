from django.contrib import admin

from .models import Discount, Item, Order, Tax


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'currency']
    list_filter = ['currency']
    search_fields = ['name', 'description']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    filter_horizontal = ['items']


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ['name', 'percent_off', 'stripe_coupon_id']
    readonly_fields = ['stripe_coupon_id']


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ['name', 'rate', 'stripe_tax_rate_id']
    readonly_fields = ['stripe_tax_rate_id']
