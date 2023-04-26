from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomerManager

class Customer(AbstractUser):
    phone = models.CharField(max_length=20, unique=True, blank=False)
    is_verified = models.BooleanField(default=False)
    email = models.EmailField(unique=True)
    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']

    objects = CustomerManager()

    def __str__(self):
        return self.email
    
    
