from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.contrib.auth import get_user_model
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
# Roles Model
class Role(models.Model):
    ROLE_CHOICES = [
        ('employee', 'Employee'),
        ('manager', 'Manager'),
        ('hradmin', 'HR Admin'),
    ]
    
    name = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        unique=True,
    )
    description = models.TextField(
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(
        default=True,    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'roles'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        ordering = ['name']
    def __str__(self):
        return self.get_name_display()
    
# Employee Designation Table
class EmployeeDesignation(models.Model):
    designationName = models.CharField(max_length=20, unique=True, blank=False)

    class Meta:
        ordering = ['designationName']

    def __str__(self):
        return self.designationName
class TeamName(models.Model):
    name = models.CharField(max_length=50, unique=True)
    active = models.BooleanField(default=True)
    total_members = models.PositiveIntegerField(default=0)
    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
User = get_user_model()

class Employee(models.Model):
    EMPLOYMENT_STATUS = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('terminated', 'Terminated'),
        ('on_leave', 'On Leave'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    # Link to CustomUser (One-to-One relationship)
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='employee_profile'
    )
    
    # Foreign Key relationships to other models
    role = models.ForeignKey(
        'Role',
        on_delete=models.PROTECT,
        related_name='employees'
    )
    
    designation = models.ForeignKey(
        'EmployeeDesignation',
        on_delete=models.PROTECT,
        related_name='employees'
    )
    
    team = models.ForeignKey(
        'TeamName',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='team_members'
    )
    
    # Employee specific fields
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique employee identifier"
    )
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True
    )
    
    employment_status = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_STATUS,
        default='active'
    )
    
    # Manager relationship (self-referencing foreign key)
   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'employees'
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
        ordering = ['employee_id']
        
        # Ensure unique combinations
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                name='unique_user_employee'
            )
        ]
    
    def __str__(self):
        return self.employee_id
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    def get_is_active(self):
        """Return the full name from the related user"""
        return self.employment_status