from django.contrib import admin
from .models import Wishlist, Coupon
# Register your models here.

class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'valid_from', 'valid_till', 'discount', 'active']
    list_filter = ['active', 'valid_from', 'valid_till']
    search_fields = ['code']


admin.site.register(Wishlist)
admin.site.register(Coupon, CouponAdmin)