from rest_framework import serializers
from home.models import Announcement, Holiday
from corevolthrm.models import Employee

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

class BirthdaySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    birth_day = serializers.SerializerMethodField()
    birth_month = serializers.SerializerMethodField()
    designation_name = serializers.SerializerMethodField()

    def get_name(self, model_obj):
        first_name = model_obj.user.first_name
        last_name = model_obj.user.last_name
        return f"{first_name} {last_name}"
    
    def get_birth_day(self, model_obj):
        return model_obj.birthday.day
    
    def get_birth_month(self, model_obj):
        return model_obj.birthday.month
    
    def get_designation_name(self, model_obj):
        return model_obj.designation.designationName
        
    class Meta:
        model = Employee
        fields = ['name', 'birth_day', 'birth_month', 'designation_name']