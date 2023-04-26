from django.db import models
from store.models import ProductVariant
from dashboard.models import Customer
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.

class Wishlist(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.variant.product.name} in {self.customer.first_name}'s wishlist"
    
class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    valid_from = models.DateTimeField()
    valid_till = models.DateTimeField()
    discount = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(50)])
    created_on = models.DateTimeField(auto_now_add=True)

    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code