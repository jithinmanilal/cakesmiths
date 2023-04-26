from django.db import models
from dashboard.models import Customer
from django.urls import reverse

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=500, blank=True)
    cat_img = models.ImageField(upload_to='category/', blank=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'
    
    def get_url(self):
        return reverse('store:product_list_by_category', args=[self.slug])

    def __str__(self):
        return self.name

class Size(models.Model):
    name = models.CharField(max_length=20)
    slug = models.SlugField(max_length=20)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/', default='default.png')
    created_on = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=False, max_length=1000)
    summary = models.TextField(null=False, max_length=250)

    class Meta:
        ordering = ['category__name', 'name']

    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField()
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} ({self.size.name})"
    
    def get_price(self, size):
        return self.price

class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.cart_id

class CartItem(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        return self.variant.price * self.quantity

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"
