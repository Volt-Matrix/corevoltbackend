from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin
from corevolthrm.models import Announcement,Role,EmployeeDesignation,TeamName,Employee
admin.site.register(CustomUser)

# Register your models here.
admin.site.register(Announcement)
admin.site.register(Role)
admin.site.register(EmployeeDesignation)
admin.site.register(TeamName)
admin.site.register(Employee)
