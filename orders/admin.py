from django.contrib import admin
from .models import Payment, Order, OrderProduct, Address
# Register your models here.

class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'payment', 'order_number', 'status']
    list_filter = ['user', 'payment', 'order_number', 'status']


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)
admin.site.register(Payment)
admin.site.register(Address)