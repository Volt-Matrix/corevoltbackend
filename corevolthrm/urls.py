from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views
from .views import LeaveRequestListAPIView, UpdateLeaveStatusAPIView
from rest_framework import routers

from .views import LeaveApplicationListCreate, LeaveApplicationDetail
from .views import approve_leave, reject_leave
from .views import total_users_count



urlpatterns = [
    path('profile/', views.profile_list),
    path('register/',views.RegisterView),
    path('login/',views.loginUser),
    path('csrf/',views.get_csrf_token),
    path('refresh/', views.refresh_view),
    path('test/',views.test_authenticated_view),
    path('logout/',views.logoutUser),
    path('api/leave-requests/', LeaveRequestListAPIView.as_view(), name='leave-request-list'),
    path('api/leave-requests/<int:pk>/', UpdateLeaveStatusAPIView.as_view(), name='update-leave-status'),
    path('api/total-users/', total_users_count),
    
    path('announcements/', views.AnnouncementList.as_view()),

    path('leave/', LeaveApplicationListCreate.as_view(), name='leave-list'),
    path('leave/<int:pk>/', LeaveApplicationDetail.as_view(), name='leave-detail'),
    path('leave/<int:pk>/approve/', approve_leave, name='leave-approve'),
    path('leave/<int:pk>/reject/', reject_leave, name='leave-reject'),
    
    
]

urlpatterns = format_suffix_patterns(urlpatterns)