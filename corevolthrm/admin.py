from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, LeaveApplication
from corevolthrm.models import Role,EmployeeDesignation,TeamName,Employee,WorkSession,Break,LeaveRequest,TimeSheetDetails


@admin.register(LeaveApplication)
class LeaveApplicationAdmin(admin.ModelAdmin):
    list_display = ('get_user_fullname', 'leaveType', 'startDate', 'endDate', 'status')
    list_filter = ('leaveType', 'status')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'reason')

    def get_user_fullname(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_user_fullname.short_description = 'Employee Name'


# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Role)
admin.site.register(EmployeeDesignation)
admin.site.register(TeamName)
admin.site.register(Employee)
admin.site.register(WorkSession)
admin.site.register(Break)
admin.site.register(LeaveRequest)
admin.site.register(TimeSheetDetails)

