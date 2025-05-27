from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views
from .views import ProfilesView,ProfilesDetailView


urlpatterns = [
    path('profile/', views.profile_list),
    path('register/',views.RegisterView),
    path('login/',views.loginUser),
    path('csrf/',views.get_csrf_token),
    path('refresh/', views.refresh_view),
    path('test/',views.test_authenticated_view),
    path('logout/',views.logoutUser),
    path('announcements/', views.AnnouncementList.as_view()),
    path('profiles/', ProfilesView.as_view(), name='profile-list'),
    path('profiles/<int:pk>/', ProfilesDetailView.as_view(), name='profile-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)