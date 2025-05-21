from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin
from corevolthrm.models import Announcement
admin.site.register(CustomUser)

# Register your models here.
admin.site.register(Announcement)