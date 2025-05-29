from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from datetime import date, timedelta
from home.models import Announcement, Holiday
from corevolthrm.models import Employee
from home.serializers import AnnouncementSerializer, HolidaySerializer, BirthdaySerializer

# Create your views here.
class AnnouncementList(generics.ListCreateAPIView):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated]

class HolidayList(generics.ListAPIView):
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    permission_classes = [IsAuthenticated]

class BirthdayList(generics.ListAPIView):
    queryset = Employee.objects.all()
    serializer_class = BirthdaySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset
        
        today = date.today()
        end_date = today + timedelta(days=120)

        # include birthdays from today to end of this month
        q1 = Q(birthday__month = today.month, birthday__day__gte = today.day)

        # include birthdays from `end month`
        q2 = Q(birthday__month = end_date.month, birthday__day__lte = end_date.day)

        # include birthdays for months in between

        # case 1: end_date is in same year as today
        if end_date.year == today.year:
            q_mid_months = Q(birthday__month__gt = today.month, birthday__month__lt = end_date.month)
        # case 2: end_date is in next year compared to today
        if end_date.year > today.year:
            q_mid_months = Q(birthday__month__gt = today.month) | Q(birthday__month__lt = end_date.month)
        
        final_q = q1 | q2 | q_mid_months


        return queryset.filter(final_q)