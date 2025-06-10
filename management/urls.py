from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from management import views

urlpatterns = [
   
    path('management/', views.Management.as_view()),
   
]

urlpatterns = format_suffix_patterns(urlpatterns)