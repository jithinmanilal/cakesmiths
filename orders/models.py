from django.db import models
from dashboard.models import Customer
from store.models import ProductVariant
from coupon.models import Coupon
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.
class Payment(models.Model):
    STATUS_P = (
        ('Pending' , 'Pending'),
        ('Failed', 'Failed'),
        ('Completed', 'Completed'),
        ('Refunded', 'Refunded'),
    )
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100)
    status = models.CharField(max_length=30, choices=STATUS_P, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id

class Address(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=50)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pin = models.CharField(max_length=10)
    user = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.first_name 

class Order(models.Model):
    STATUS = (
        ('Submitted' , 'Submitted'),
        ('Confirmed', 'Confirmed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Return', 'Return'),
        ('Cancel', 'Cancel'),
        ('Cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    order_number = models.CharField(max_length=20)
    order_total = models.FloatField()
    status = models.CharField(max_length=30, choices=STATUS, default='Submitted')
    ip = models.CharField(blank=True, max_length=20)
    is_ordered = models.BooleanField(default=True)

    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)
    discount = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(50)])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def full_name(self):
        return f'{self.address.first_name} {self.address.last_name}'

    def full_address(self):
        return f'{self.address.address_line_1} {self.address.address_line_2}'
    
    def order_products(self):
        return OrderProduct.objects.filter(order=self)

    def __str__(self):
        return self.user.first_name
    
class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.variant.product.name

