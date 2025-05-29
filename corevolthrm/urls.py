from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views
from .views import ProfilesView,ProfilesDetailView

from .views import LeaveApplicationListCreate, LeaveApplicationDetail
from django.conf import settings
from django.conf.urls.static import static
from .views import approve_leave, reject_leave

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
    path('leave/', LeaveApplicationListCreate.as_view(), name='leave-list'),
    path('leave/<int:pk>/', LeaveApplicationDetail.as_view(), name='leave-detail'),
    path('leave/<int:pk>/approve/', approve_leave, name='leave-approve'),
    path('leave/<int:pk>/reject/', reject_leave, name='leave-reject'),
    path('link-employee/',views.AddEmployee),
    path('employee/clock-in/',views.clock_in),
    path('employee/checkIn-check/',views.check_clockIn),
    path('employee/clock_out/',views.clock_out)
]

urlpatterns = format_suffix_patterns(urlpatterns)
