from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from home import views

urlpatterns = [
    path('announcements/', views.AnnouncementList.as_view()),
    path('holidays/', views.HolidayList.as_view()),
    path('birthdays/', views.BirthdayList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)