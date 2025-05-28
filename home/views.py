from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.db.models.functions import Extract

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
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset
        
        return super().get_queryset()