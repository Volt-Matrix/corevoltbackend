from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.conf import settings

from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from datetime import datetime
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
    
class LeaveApplication(models.Model):
    LEAVE_TYPES = [
        ("Sick", "Sick Leave"),
        ("Casual", "Casual Leave"),
        ("Earned", "Earned Leave"),
    ]
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="leave_applications")
    leaveType = models.CharField(max_length=10, choices=LEAVE_TYPES)
    startDate = models.DateField()
    endDate = models.DateField()
    reason = models.TextField()
    contactDuringLeave = models.CharField(max_length=100, blank=True)
    attachment = models.FileField(upload_to="attachments/", null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending")

    def __str__(self):
        return f"{self.user.email} - {self.leaveType} ({self.startDate} to {self.endDate})"

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

class Profiles(models.Model):
    employee_id = models.CharField(max_length=10, unique=True)
    full_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)  # Make DOB optional
    email = models.EmailField()
    phone = models.IntegerField()
    alt_phone = models.IntegerField(blank=True, null=True)  # Optional
    current_address = models.CharField(max_length=200)
    permanent_address = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zip_code = models.IntegerField()
    country = models.CharField(max_length=50)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return self.full_name

class UploadDocument(models.Model):
    DOC_TYPE_CHOICES = [
        ('Aadhar Card', 'Aadhar Card'),
        ('Driving Licence', 'Driving Licence'),
        ('PAN Card', 'PAN Card'),
        ('Passport', 'Passport'),
        ('Education', 'Education'),
        ('Experience', 'Experience'),
    ]

    doc_type = models.CharField(max_length=20, choices=DOC_TYPE_CHOICES)
    degree = models.CharField(max_length=255, blank=True, null=True)
    institute = models.CharField(max_length=255, blank=True, null=True)

    job_title = models.CharField(max_length=255, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    duration = models.CharField(max_length=255, blank=True, null=True)

    file = models.FileField(upload_to='upload-documents/')
    profile = models.ForeignKey(Profiles, on_delete=models.CASCADE, related_name='documents')

    def __str__(self):
        return f'{self.doc_type} for {self.profile}'



class TeamName(models.Model):
    name = models.CharField(max_length=50, unique=True)
    active = models.BooleanField(default=True)
    manager = models.ForeignKey(
        'Employee', 
        on_delete=models.CASCADE, 
        related_name='managed_teams',
        help_text="Employee who manages this team", 
        null=True,
        blank=True 
    )
    members = models.ManyToManyField(
        'Employee',
        related_name='teams',
        blank=True,
        help_text="Team members"
    )
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
        related_name='employee_obj'
    )

    profile = models.OneToOneField(
        'Profiles',
        on_delete=models.CASCADE,
        related_name='employee_profile',
        null=True,
        blank=True  # Optional if you want to allow employees without profile yet
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

    birthday = models.DateField(blank = True, null = True, default = datetime(day=1, month=1, year=1990).date())
    
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
class WorkSession(models.Model):
    LEAVE_STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Submitted','Submitted')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    clock_in = models.DateTimeField()
    clock_out = models.DateTimeField(null=True, blank=True)
    total_work_time = models.DurationField(null=True, blank=True)  # New field
    approval_status=  models.CharField(max_length=20, choices=LEAVE_STATUS_CHOICES, default='Pending')
    next_clock_in = models.DateTimeField(null=True,blank=True)

    def is_active(self):
        return self.clock_out is None

    def total_break_time(self):
        return sum((b.end - b.start for b in self.break_set.all() if b.end), timedelta())

class Break(models.Model):
    work_session = models.ForeignKey(WorkSession, on_delete=models.CASCADE)
    start = models.DateTimeField()
    end = models.DateTimeField(null=True, blank=True)

    def is_active(self):
        return self.end is None
class LeaveRequest(models.Model):
    LEAVE_TYPES = [
        ('Sick', 'Sick'),
        ('Casual', 'Casual'),
        ('Earned', 'Earned'),
        # add more as needed
    ]

    LEAVE_STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='leave_requests')
    department = models.CharField(max_length=100,blank=True,null=True)
    leaveType = models.CharField(max_length=50,choices=LEAVE_TYPES)
    startDate = models.DateField()
    endDate= models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=LEAVE_STATUS_CHOICES, default='Pending')
    applied_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.leaveType} ({self.status})"
    

class TimeSheetDetails(models.Model):
    session = models.ForeignKey(WorkSession,on_delete=models.CASCADE,related_name='timesheet_details',null=True)
    hourSpent = models.IntegerField()
    description = models.CharField() 
    def __str__(self):
        return self.description