from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin
admin.site.register(CustomUser)
admin.site.register(CustomUser)
from .models import LeaveApplication

@admin.register(LeaveApplication)
class LeaveApplicationAdmin(admin.ModelAdmin):
    list_display = ('get_user_fullname', 'leaveType', 'startDate', 'endDate', 'status')
    def get_user_fullname(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_user_fullname.short_description = 'Employee Name'
    list_filter = ('leaveType', 'status')
    search_fields = ('employeeId', 'reason')