from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.profile_list),
    path('register/',views.RegisterView),
    path('login/',views.loginUser),
    path('csrf/',views.get_csrf_token),
    path('refresh/', views.refresh_view),
    path('test/',views.test_authenticated_view),
    path('logout/',views.logoutUser)

]