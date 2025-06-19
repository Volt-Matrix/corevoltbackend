from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views
from .views import ProfilesView,ProfilesDetailView

from .views import LeaveApplicationListCreate, LeaveApplicationDetail,LeaveRequestListAPIView,UpdateLeaveStatusAPIView,UploadDocumentView,EmployeeListAPIView
from django.conf import settings
from django.conf.urls.static import static
from .views import approve_leave, reject_leave,total_users_count
from .views import get_team_hierarchy

urlpatterns = [
    path('profile/', views.profile_list),
    path('register/',views.RegisterView),
    path('login/',views.loginUser),
    path('csrf/',views.get_csrf_token),
    path('refresh/', views.refresh_view),
    path('test/',views.test_authenticated_view),
    path('logout/',views.logoutUser),
    path('profiles/', ProfilesView.as_view(), name='profile-list'),
    path('profiles/<int:pk>/', ProfilesDetailView.as_view(), name='profile-detail'),
    path('upload-documents/', UploadDocumentView.as_view(), name='upload-documents'),
    path('employees/', EmployeeListAPIView.as_view(), name='employee-list'),
    # path('employee-by-email/', employee_by_email, name='employee-by-email'),
    path('leave/', LeaveApplicationListCreate.as_view(), name='leave-list'),
    path('leave/<int:pk>/', LeaveApplicationDetail.as_view(), name='leave-detail'),
    path('leave/<int:pk>/approve/', approve_leave, name='leave-approve'),
    path('leave/<int:pk>/reject/', reject_leave, name='leave-reject'),
    path('link-employee/',views.AddEmployee),
    path('employee/clock-in/',views.clock_in),
    path('employee/checkIn-check/',views.check_clockIn),
    path('employee/clock_out/',views.clock_out),
     path('api/leave-requests/', LeaveRequestListAPIView.as_view(), name='leave-request-list'),
    path('api/leave-requests/<int:pk>/', UpdateLeaveStatusAPIView.as_view(), name='update-leave-status'),
    path('api/total-users/', total_users_count),
    path('my_sessions/',views.my_session),
    path("api/team-hierarchy/", get_team_hierarchy, name="team-hierarchy"),
    path('time-sheet-details/',views.time_sheet_detail),
    path('daily-log/',views.daily_log),
    path('daily-log-delete-expense/<int:session_id>/<int:expense_id>/',views.delete_expense_daily_log),
    path('attendance-add-time-expense/',views.add_time_expense),
    path('submit-timesheet/<int:sessionId>/',views.submit_time_Sheet)
]

urlpatterns = format_suffix_patterns(urlpatterns)
