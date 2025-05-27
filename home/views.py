from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from home.models import Announcement, Holiday
from home.serializers import AnnouncementSerializer, HolidaySerializer

# Create your views here.
class AnnouncementList(generics.ListCreateAPIView):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated]

class HolidayList(generics.ListAPIView):
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    # permission_classes = [IsAuthenticated]