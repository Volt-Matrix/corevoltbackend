from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views
from .views import LeaveRequestListAPIView, LeaveRequestUpdateAPIView
from rest_framework import routers



urlpatterns = [
    path('profile/', views.profile_list),
    path('register/',views.RegisterView),
    path('login/',views.loginUser),
    path('csrf/',views.get_csrf_token),
    path('refresh/', views.refresh_view),
    path('test/',views.test_authenticated_view),
    path('logout/',views.logoutUser),
    path('api/leave-requests/', LeaveRequestListAPIView.as_view(), name='leave-request-list'),
    path('leaves/<int:pk>/', LeaveRequestUpdateAPIView.as_view(), name='leave-request-update'),

    
    path('announcements/', views.AnnouncementList.as_view()),
    
    
]

urlpatterns = format_suffix_patterns(urlpatterns)