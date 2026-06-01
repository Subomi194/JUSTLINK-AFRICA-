from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, password=None, **extra_fields): 
        email = extra_fields.pop('email', None)

        if email:
            email = self.normalize_email(email) 
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields): # The create_superuser method is responsible for creating a superuser. It takes an email, password, and any additional fields as arguments. It sets the is_staff and is_superuser fields to True, checks if they are set correctly, and then calls the create_user method to create the superuser.
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')  # Set role to 'admin' for superusers

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        extra_fields['email'] = email  # Ensure email is included in extra_fields
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('lawyer', 'Lawyer'),
        ('admin', 'Admin'),
    )

    email = models.EmailField(unique=True, null=True, blank=True)
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES) 
    language = models.CharField(max_length=20, default='en')
    country = models.CharField(max_length=100)
    ussd_session_id = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'role', 'country', 'phone_number', 'language']

    def __str__(self):
        return self.email or self.name or str(self.id)

class LawyerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lawyer_profile')
    law_firm = models.CharField(max_length=255)
    license_number = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"{self.user.name}'s Lawyer Profile"

