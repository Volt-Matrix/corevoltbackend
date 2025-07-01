from django.urls import path, include
from rest_framework.routers import DefaultRouter
from employee_structure import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'projects', views.ProjectViewSet, basename='project')
router.register(r'teams', views.TeamViewSet, basename='team')

urlpatterns = [
    path('management/', include(router.urls)), # For Projects and Teams
    path('management/roles/', views.RoleListAPIView.as_view(), name='role-list'),
    path('management/employees-roles/', views.EmployeeRoleListAPIView.as_view(), name='employee-role-list'),
    path('management/employees/<int:employee_id>/update-role/', views.EmployeeRoleUpdateAPIView.as_view(), name='employee-role-update'),
    path('management/all-employees/', views.AllEmployeesListAPIView.as_view(), name='all-employees-list'),
]