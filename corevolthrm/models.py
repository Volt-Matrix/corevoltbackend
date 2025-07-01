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
    department = models.ForeignKey(
        'TeamName',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leave_requests',
        help_text="Team (department) to which the employee belongs"
    )
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
    


class AssetRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='asset_requests')
    asset_type = models.ForeignKey('Asset', on_delete=models.CASCADE, null=True)
    description = models.TextField()
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='Pending')

    def __str__(self):
        return f"Request by {self.user.email} for {self.category}"


class AssetCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Asset(models.Model):
    category = models.ForeignKey(AssetCategory, on_delete=models.CASCADE, related_name='assets')
    assetName = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    total = models.PositiveIntegerField()
    available = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=[('Active', 'Active'), ('Inactive', 'Inactive')])

    def __str__(self):
        return f"{self.category.name}: {self.assetName}"
    
    def save(self, *args, **kwargs):
        from .models import AssetList  

        is_new = self.pk is None
        prev_total = 0

        if not is_new:
            try:
                prev_total = Asset.objects.get(pk=self.pk).total
            except Asset.DoesNotExist:
                pass

        super().save(*args, **kwargs)  

        # Add new AssetList items if total increased
        if self.total > prev_total:
            current_items = AssetList.objects.filter(asset=self)
            existing_ids = set(current_items.values_list('assetId', flat=True))

            prefix = self.assetName[:3].upper()
            index = 1
            added = 0
            to_add = self.total - prev_total

            while added < to_add:
                new_id = f"{prefix}-{self.pk}-{index:03}"
                if new_id not in existing_ids:
                    AssetList.objects.create(
                        asset=self,
                        assetName=self.assetName,
                        assetId=new_id,
                        status="Available"
                    )
                    added += 1
                index += 1

        elif self.total < prev_total:
            to_remove = prev_total - self.total
            removable_items = list(AssetList.objects.filter(asset=self, status="Available").order_by('-id')[:to_remove])
            count_removed = len(removable_items)

            if count_removed < to_remove:
                print(f"Only {count_removed} available assets found to delete (needed {to_remove})")

            for item in removable_items:
                item.delete()


    def update_total_and_available(self):
    
        total = self.asset_items.count()
        available = self.asset_items.filter(status="Available").count()
        Asset.objects.filter(pk=self.pk).update(total=total, available=available)
class AssetList(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='asset_items',null=True,blank=True)  
    assetName = models.CharField(max_length=100)
    assetId = models.CharField(max_length=50, unique=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ("Available", "Available"),
            ("Assigned", "Assigned"),
            ("In Repair", "In Repair"),
            ("Retired", "Retired"),
            ("Lost", "Lost"),
        ],
        default="Available"
    )
    assignedTo = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_assets'
    )
    assignedDate = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.assetName} ({self.assetId})"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.asset:
            self.asset.update_total_and_available()
    
    def delete(self, *args, **kwargs):
        asset = self.asset 
        super().delete(*args, **kwargs)
        if asset:
            asset.update_total_and_available()