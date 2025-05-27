from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin
from corevolthrm.models import Announcement,LeaveRequest
admin.site.register(CustomUser)

# Register your models here.
admin.site.register(Announcement)


class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'from_date', 'to_date', 'status')
    list_filter = ('status',)
    search_fields = ('user__email',)


    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return True

    
    def has_delete_permission(self, request, obj=None):
        return False
    
admin.site.register(LeaveRequest, LeaveRequestAdmin)
