from rest_framework import serializers
from corevolthrm.models import Employee, WorkSession, TeamName
from django.utils import timezone
from datetime import timedelta

# NEW: Serializer for individual work sessions in the expanded view
class DailyWorkSessionDetailSerializer(serializers.ModelSerializer):
    total_work_time_seconds = serializers.SerializerMethodField()

    class Meta:
        model = WorkSession
        fields = ['clock_in', 'clock_out', 'total_work_time_seconds'] # Using total_work_time_seconds for consistency

    def get_total_work_time_seconds(self, obj):
        if obj.total_work_time:
            return int(obj.total_work_time.total_seconds())
        # If clock_out is null but clock_in exists (live session)
        if obj.clock_in and obj.clock_out is None:
             # Calculate duration up to now, or return specific indicator.
             # For a completed list, this might not be needed if only completed sessions shown,
             # or if showing live duration, calculate: timezone.now() - obj.clock_in
             return int((timezone.now() - obj.clock_in).total_seconds()) # Example for live duration
        return 0 # if no duration available

# NEW: Serializer for each row in the main attendance overview table
class AttendanceOverviewRowSerializer(serializers.Serializer):
    employee_id = serializers.CharField()
    name = serializers.CharField()
    department_name = serializers.CharField(allow_null=True, required=False) # From Employee's team
    most_recent_clock_in = serializers.DateTimeField(allow_null=True)
    most_recent_clock_out = serializers.DateTimeField(allow_null=True)
    total_daily_worked_seconds = serializers.IntegerField()
    status = serializers.CharField() # Present, Absent
    sessions = DailyWorkSessionDetailSerializer(many=True) # List of all sessions for the day

# NEW: Serializer for TeamName (to be used as Department filter)
class TeamNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamName
        fields = ['id', 'name']