from rest_framework import serializers
from home.models import Announcement, Holiday

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__'

class HolidaySerializer(serializers.ModelSerializer):
    day_of_the_week = serializers.SerializerMethodField()

    def get_day_of_the_week(self, obj):
        return obj.date.strftime("%A")

    class Meta:
        model = Holiday
        fields = ['name', 'date', 'day_of_the_week']