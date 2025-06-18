from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.utils.dateparse import parse_date
from django.utils import timezone
from datetime import datetime, time
from datetime import time as dt_time
from django.db.models import Q, Sum
from corevolthrm.models import Employee, WorkSession, TeamName
from attendance.serializers import DailyWorkSessionDetailSerializer, AttendanceOverviewRowSerializer, TeamNameSerializer
from corevolthrm.customPermission.customPermissionClasss import IsManagerOrAdmin
User = get_user_model()

# Create your views here.
# API View for Attendance Overview Data
class AttendanceOverviewAPIView(APIView):
    permission_classes = [IsAuthenticated,IsManagerOrAdmin]

    def get(self, request, *args, **kwargs):
        date_param = request.query_params.get('date', timezone.now().strftime('%Y-%m-%d'))
        target_date = parse_date(date_param)

        if not target_date:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        team_id_param = request.query_params.get('department_id')
        search_query = request.query_params.get('search')

        employees_queryset = Employee.objects.select_related('user', 'team').all()

        if team_id_param:
            employees_queryset = employees_queryset.filter(team_id=team_id_param)
        
        if search_query:
            employees_queryset = employees_queryset.filter(
                Q(employee_id__icontains=search_query) |
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(user__email__icontains=search_query)
            )
        
        start_of_day = timezone.make_aware(datetime.combine(target_date, dt_time.min), timezone.get_default_timezone())
        end_of_day = timezone.make_aware(datetime.combine(target_date, dt_time.max), timezone.get_default_timezone())

        overview_data_for_serializer = []
        first_check_in_times_seconds_list = [] # To store first check-in times in seconds from midnight
        
        # get the original timezone to restore it later
        original_current_timezone_obj = timezone.get_current_timezone()
        ist_timezone_str = 'Asia/Kolkata'

        try:
            timezone.activate(ist_timezone_str)

            for emp in employees_queryset:
                daily_sessions_queryset = WorkSession.objects.filter(
                    user=emp.user,
                    clock_in__gte=start_of_day,
                    clock_in__lte=end_of_day 
                ).order_by('clock_in')

                total_daily_actual_work_seconds = 0
                most_recent_ci = None
                most_recent_co = None
                status = "Absent"

                if daily_sessions_queryset.exists():
                    status = "Present"
                    
                    # Get first check-in time for average calculation
                    first_session_instance = daily_sessions_queryset.first()
                    if first_session_instance and first_session_instance.clock_in:
                        # Convert to server's local time to get consistent time part
                        local_first_check_in = timezone.localtime(first_session_instance.clock_in)
                        time_part = local_first_check_in.time()
                        seconds_from_midnight = time_part.hour * 3600 + time_part.minute * 60 + time_part.second
                        first_check_in_times_seconds_list.append(seconds_from_midnight)

                    for session_instance in daily_sessions_queryset:
                        if session_instance.total_work_time:
                            total_daily_actual_work_seconds += int(session_instance.total_work_time.total_seconds())

                    last_model_session = daily_sessions_queryset.last()
                    if last_model_session:
                        most_recent_ci = last_model_session.clock_in
                        most_recent_co = last_model_session.clock_out
                
                overview_data_for_serializer.append({
                    'employee_id': emp.employee_id,
                    'name': f"{emp.user.first_name} {emp.user.last_name}",
                    'department_name': emp.team.name if emp.team else None,
                    'most_recent_clock_in': most_recent_ci,
                    'most_recent_clock_out': most_recent_co,
                    'total_daily_worked_seconds': total_daily_actual_work_seconds,
                    'status': status,
                    'sessions': daily_sessions_queryset,
                })
        finally:
            # restore original timezone object
            timezone.activate(original_current_timezone_obj)

        # Calculate average check-in time
        average_check_in_time_str = None
        if first_check_in_times_seconds_list:
            avg_seconds = sum(first_check_in_times_seconds_list) / len(first_check_in_times_seconds_list)
            avg_hour = int(avg_seconds // 3600)
            avg_minute = int((avg_seconds % 3600) // 60)
            
            # Format as HH:MM AM/PM (example formatting)
            avg_time_obj = dt_time(hour=avg_hour, minute=avg_minute)
            average_check_in_time_str = avg_time_obj.strftime("%I:%M %p")


        employee_attendance_list = AttendanceOverviewRowSerializer(instance=overview_data_for_serializer, many=True).data
        
        # Structure the final response
        final_response_data = {
            "summary_stats": {
                "average_check_in_time": average_check_in_time_str,
                "total_present": sum(1 for e in employee_attendance_list if e['status'] == 'Present'),
                "total_absent": sum(1 for e in employee_attendance_list if e['status'] == 'Absent'),
            },
            "employee_attendance_list": employee_attendance_list
        }
        
        return Response(final_response_data)

# API View for listing Teams (Departments)
class TeamListView(generics.ListAPIView):
    queryset = TeamName.objects.filter(active=True).order_by('name') # Filter active teams
    serializer_class = TeamNameSerializer
    permission_classes = [IsAuthenticated]