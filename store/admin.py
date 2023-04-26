from django.contrib import admin
from .models import Product, Category, Size, ProductVariant, Cart, CartItem
# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug')

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'created_on')
    prepopulated_fields = {'slug' : ('name',)}

class SizeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug')

admin.site.register(Product, ProductAdmin),
admin.site.register(Category, CategoryAdmin),
admin.site.register(Size),
admin.site.register(ProductVariant),
admin.site.register(Cart),
admin.site.register(CartItem),


