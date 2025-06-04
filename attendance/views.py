from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.utils.dateparse import parse_date
from django.utils import timezone
from datetime import datetime, time
from django.db.models import Q, Sum
from corevolthrm.models import Employee, WorkSession, TeamName
from attendance.serializers import DailyWorkSessionDetailSerializer, AttendanceOverviewRowSerializer, TeamNameSerializer

User = get_user_model()

# Create your views here.
# API View for Attendance Overview Data
class AttendanceOverviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        date_param = request.query_params.get('date', timezone.now().strftime('%Y-%m-%d'))
        target_date = parse_date(date_param)

        if not target_date:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        team_id_param = request.query_params.get('department_id') # Frontend sends department_id
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
        
        start_of_day = timezone.make_aware(datetime.combine(target_date, time.min), timezone.get_default_timezone())
        end_of_day = timezone.make_aware(datetime.combine(target_date, time.max), timezone.get_default_timezone())

        # This list will hold dictionaries, where 'sessions' will contain model instances (QuerySet)
        overview_data_for_serializer = [] 
        
        for emp in employees_queryset:
            # Fetch WorkSession model instances for this employee on the target date
            daily_sessions_queryset = WorkSession.objects.filter(
                user=emp.user, # WorkSession.user is FK to CustomUser
                clock_in__gte=start_of_day,
                clock_in__lte=end_of_day 
            ).order_by('clock_in')

            total_daily_actual_work_seconds = 0
            most_recent_ci = None
            most_recent_co = None
            status = "Absent"

            if daily_sessions_queryset.exists():
                status = "Present"
                
                # Calculate total daily work from the 'total_work_time' field of model instances
                # This field is a DurationField and is typically set when a session is clocked out.
                for session_instance in daily_sessions_queryset:
                    if session_instance.total_work_time:
                        total_daily_actual_work_seconds += int(session_instance.total_work_time.total_seconds())
                    # If an active session's current duration should be added to the daily total:
                    # elif session_instance.clock_in and session_instance.clock_out is None:
                    #     total_daily_actual_work_seconds += int((timezone.now() - session_instance.clock_in).total_seconds())


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

        # AttendanceOverviewRowSerializer will now receive the 'sessions' field 
        # as a QuerySet. Its nested DailyWorkSessionDetailSerializer(many=True)
        # will then correctly iterate over these WorkSession model instances.
        serializer = AttendanceOverviewRowSerializer(instance=overview_data_for_serializer, many=True)
        return Response(serializer.data)

# API View for listing Teams (Departments)
class TeamListView(generics.ListAPIView):
    queryset = TeamName.objects.filter(active=True).order_by('name') # Filter active teams
    serializer_class = TeamNameSerializer
    permission_classes = [IsAuthenticated]