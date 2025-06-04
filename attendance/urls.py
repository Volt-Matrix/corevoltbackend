from django.urls import path
from attendance import views

urlpatterns = [
    path('attendance-overview/', views.AttendanceOverviewAPIView.as_view(), name = 'attendance-overview'),
    path('teams/', views.TeamListView.as_view(), name = 'list-teams'),
]