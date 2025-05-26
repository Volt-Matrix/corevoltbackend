from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager

# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)
class CustomUser(AbstractUser):
    username = None  # Remove username field
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone']
    
    objects = CustomUserManager()
    
    def __str__(self):
        return self.email
    
class Announcement(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=False)
    content = models.TextField()

    class Meta:
        ordering = ['-created']

class Holiday(models.Model):
    name = models.CharField(max_length = 30, blank=False)
    date = models.DateField()

    class Meta:
        ordering = ['date']