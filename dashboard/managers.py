from django.contrib.auth.models import BaseUserManager

class CustomerManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, phone, password = None, **extra_fields):
        if not phone:
            raise ValueError('Phone number is required.')
        
        user = self.model(phone = phone, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, phone, password = None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(phone, password, **extra_fields)
