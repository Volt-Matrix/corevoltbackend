from django.contrib import admin
from .models import CustomUser,LeaveApplication
from django.contrib.auth.admin import UserAdmin
from corevolthrm.models import Announcement,LeaveRequest
admin.site.register(CustomUser)

# Register your models here.
admin.site.register(Announcement)

@admin.register(LeaveApplication)
class LeaveApplicationAdmin(admin.ModelAdmin):
    list_display = ('get_user_fullname', 'leaveType', 'startDate', 'endDate', 'status')
    list_filter = ('leaveType', 'status')
    search_fields = ('user_first_name', 'userlast_name', 'user_email', 'reason')

    def get_user_fullname(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_user_fullname.short_description = 'Employee Name'



