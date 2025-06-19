from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import status,viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserRegistrationSerializer, LeaveApplicationSerializer,EmployeeSerializer,WorkSessionSerializer,LeaveRequestSerializer,TimeSheetDetailsSerializer,UploadDocumentSerializer
from django.contrib.auth import authenticate,get_user_model
from django.views.decorators.http import require_POST
from django.middleware.csrf import get_token
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from corevolthrm.models import LeaveApplication,Employee,WorkSession,LeaveApplication,LeaveRequest,TimeSheetDetails,UploadDocument
from datetime import datetime, time,timedelta
from django.utils import timezone
from django.core import serializers
from .models import Employee, Profiles
from .serializers import ProfilesSerializer

from rest_framework.authentication import SessionAuthentication
from .customPermission.customPermissionClasss import IsManagerOrAdmin
class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return
# Create your views here.
def profile_list(request):
    if request.method == 'GET':
        return JsonResponse({"message":"Request recived"})

@csrf_exempt
def RegisterView(request):
    permission_classes = [AllowAny]
    data = json.loads(request.body)
    print(data)
    print(request.method)
    if request.method =='POST':
        serializer = UserRegistrationSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            return JsonResponse({
                "message": "User registered successfully",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "phone": user.phone
                }
            }, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@require_POST
@csrf_exempt
def loginUser(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        data = json.loads(request.body)
        email = data.get('userName')
        password = data.get('password')
        user = authenticate(request, email=email, password=password)
        employee = Employee.objects.get(user=user)
        role = str(employee.role)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            
            # Generate CSRF token
            csrf_token = get_token(request)
            
            response = JsonResponse({
                "message": "Login successful",
                "user": {
                    "firstName": user.first_name,
                    "email": user.email,
                    "isLoggedIn": True,
                    "id": user.id,
                    'role':role,
                    'permission_list':''
                },
                "csrf_token": csrf_token, 
            })
            
            # Set refresh token (7 days)
            response.set_cookie(
                key="refresh_token",
                value=str(refresh),
                httponly=True,
                secure=True,  # Use True in production
                samesite='Lax',
                max_age=7 * 24 * 60 * 60
            )

            # Set access token (15 minutes)
            response.set_cookie(
                key="access_token",
                value=str(refresh.access_token),
                httponly=True,
                secure=True,  # Use True in production
                samesite='Lax',
                max_age=60 * 60
            )

            return response
        
        return JsonResponse({"error": "Invalid credentials"}, status=401)
    
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@api_view(['GET'])
def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({"csrftoken": csrf_token})

@api_view(["POST"])
def refresh_view(request):
    refresh_token = request.COOKIES.get("refresh_token")
    if refresh_token is None:
        return JsonResponse({"error": "No refresh token provided"}, status=403)

    try:
        refresh = RefreshToken(refresh_token)
        new_access_token = str(refresh.access_token)
        response = JsonResponse({"message": "Token refreshed"})
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            secure=True,
            samesite='Lax',
            max_age=60 * 60  # 15 minutes
        )
        return response

    except Exception as e:
        return JsonResponse({"error": "Invalid refresh token"}, status=403)
    
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def test_authenticated_view(request):
   user = request.user
   print(request.user)
   return JsonResponse({
        "message": f"Hello! You are authenticated.",
        "user_id": user.id,
        "email": user.email,
    })
@csrf_exempt   
def logoutUser(request):
    response = JsonResponse({"message": "Logout successful",'isLogged':False})
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response

class ProfilesView(APIView):
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    permission_classes = [AllowAny]

    def post(self, request):
        employee_id = request.data.get("employee_id")
        if not employee_id:
            return Response({"error": "employee_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        #Find the employee
        try:
            employee = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

        #Create or update profile
        try:
            profile = Profiles.objects.get(employee_id=employee_id)
            serializer = ProfilesSerializer(profile, data=request.data)
        except Profiles.DoesNotExist:
            serializer = ProfilesSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(employee=employee)  # 🔗 Link the profile to the employee
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class ProfilesDetailView(RetrieveUpdateDestroyAPIView):
    parser_classes = (JSONParser, MultiPartParser, FormParser) 

    def get(self, request, pk):
        try:
            profile = Profiles.objects.get(pk=pk)
        except Profiles.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ProfilesSerializer(profile)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            profile = Profiles.objects.get(pk=pk)
        except Profiles.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ProfilesSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            profile = Profiles.objects.get(pk=pk)
        except Profiles.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        profile.delete()
        return Response({"message": "Profile deleted"}, status=status.HTTP_200_OK)

    
class UploadDocumentView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, *args, **kwargs):
        # List all uploaded documents
        documents = UploadDocument.objects.all()
        serializer = UploadDocumentSerializer(documents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        try:
            employee_id = request.data.get("employee_id")
            doc_type = request.data.get("doc_type")
            file = request.data.get("file")

            if not employee_id or not doc_type or not file:
                return Response(
                    {"error": "Missing required fields"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                profile = Profiles.objects.get(employee_id=employee_id)
            except Profiles.DoesNotExist:
                return Response(
                    {"error": f"No profile found with employee_id: {employee_id}"},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = UploadDocumentSerializer(data={
                "doc_type": doc_type,
                "file": file,
                "profile": profile.id
            })

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"error": f"TypeError: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
class EmployeeListAPIView(generics.ListAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
class MyEmployeeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            employee = Employee.objects.get(user=request.user)
            serializer = EmployeeSerializer(employee)
            return Response(serializer.data)
        except Employee.DoesNotExist:
            return Response({'detail': 'Employee data not found.'}, status=status.HTTP_404_NOT_FOUND)
        

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    
class LeaveApplicationListCreate(generics.ListCreateAPIView):
    serializer_class = LeaveApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return LeaveApplication.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LeaveApplicationDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LeaveApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return LeaveApplication.objects.filter(user=self.request.user)

# Approve leave
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_leave(request, pk):
    try:
        leave = LeaveApplication.objects.get(pk=pk, user=request.user)
        leave.status = "Approved"
        leave.save()
        return Response({"message": "Leave approved"}, status=status.HTTP_200_OK)
    except LeaveApplication.DoesNotExist:
        return Response({"error": "Leave not found"}, status=status.HTTP_404_NOT_FOUND)

# Reject leave
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_leave(request, pk):
    try:
        leave = LeaveApplication.objects.get(pk=pk, user=request.user)
        leave.status = "Rejected"
        leave.save()
        return Response({"message": "Leave rejected"}, status=status.HTTP_200_OK)
    except LeaveApplication.DoesNotExist:
        return Response({"error": "Leave not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(["GET"])
def AddEmployee(request):
    return JsonResponse({'message':"request received"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_clockIn(request):
    data =  WorkSession.objects.filter(user=request.user, clock_out__isnull=True)
    workSession = WorkSessionSerializer(data,many=True)
    print(workSession.data)
    res = False
    if(workSession.data):
        res = True
        return Response({'clock_in':res,'session':workSession.data},status=status.HTTP_200_OK)
    else:
        return Response({'clock_in':res},status=status.HTTP_200_OK)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def clock_in(request):
    if WorkSession.objects.filter(user=request.user, clock_in__date=timezone.localdate(),clock_out__date = timezone.localdate()).exists():
        currentlog = WorkSession.objects.get(user=request.user,clock_in__date=timezone.localdate(),clock_out__date = timezone.localdate())
        if(currentlog):
            currentlog.clock_out = None
            currentlog.next_clock_in = timezone.now()
            currentlog.save()
            workSession = WorkSessionSerializer(currentlog)
            print(workSession.data)
            return Response({'clock_in':True,'session':[workSession.data]},status=status.HTTP_200_OK)
    if not WorkSession.objects.filter(user=request.user, clock_out__isnull=True).exists():
       workSession =  WorkSession.objects.create(user=request.user, clock_in=timezone.now())
       session = WorkSessionSerializer(workSession)
       return Response({'clock_in':True,'session':[session.data]},status=status.HTTP_200_OK)
    else:
       data =  WorkSession.objects.filter(user=request.user, clock_out__isnull=True)
       workSession = WorkSessionSerializer(data,many=True)
       print(workSession.data)
       return Response({'session':workSession.data},status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])   
def clock_out(request):
    def parse_duration(duration):
    
        if isinstance(duration, timedelta):
        # Already a timedelta object
            return duration
        elif isinstance(duration, str):
        # Parse string format
            try:
            # Handle format like "0:00:02.875683"
                if '.' in duration:
                    time_part, microsec_part = duration.split('.')
                    hours, minutes, seconds = map(int, time_part.split(':'))
                    microseconds = int(microsec_part.ljust(6, '0')[:6])  # Pad or truncate to 6 digits
                    return timedelta(hours=hours, minutes=minutes, seconds=seconds, microseconds=microseconds)
                else:
                    # Handle format like "0:00:02"
                    hours, minutes, seconds = map(int, duration.split(':'))
                    return timedelta(hours=hours, minutes=minutes, seconds=seconds)
            except Exception as e:
                print(f"Error parsing duration '{duration}': {e}")
                return timedelta(0)
        else:
            print(f"Unsupported duration type: {type(duration)}")
            return timedelta(0)
           
    session = WorkSession.objects.filter(user=request.user, clock_out__isnull=True).first()
    session.clock_out = timezone.now()
    if session:
        if session.next_clock_in:
            total_time = session.clock_out - session.next_clock_in + (parse_duration(session.total_work_time) if session.total_work_time else parse_duration('00:00:00'))
            session.total_work_time = total_time 
            print('next clock in ')
        else:
            total_time = session.clock_out - session.clock_in + (parse_duration(session.total_work_time) if session.total_work_time else parse_duration('00:00:00'))
            session.total_work_time = total_time
            print('clock out')
        session.save()
        return Response({'Message':"Successfully clocked out"},status=status.HTTP_200_OK)

class LeaveRequestListAPIView(generics.ListCreateAPIView):
    queryset = LeaveApplication.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated,IsManagerOrAdmin]
   
class UpdateLeaveStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]
 
    def patch(self, request, pk):
        try:
            leave_request = LeaveApplication.objects.get(pk=pk)
            new_status = request.data.get('status')
            if new_status in ['Approved', 'Rejected']:
                leave_request.status = new_status
                leave_request.save()
                return Response({'message': 'Status updated successfully'}, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        except LeaveRequest.DoesNotExist:
            return Response({'error': 'Leave request not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def total_users_count(request):
    User = get_user_model()
    total_users = User.objects.count()
    return Response({"total_users": total_users})

@api_view(["GET"])
def my_session(request):
    WorkSessions = WorkSession.objects.filter(user=request.user)
    sessions = WorkSessionSerializer(WorkSessions,many=True)
    return Response({"sessions":sessions.data})

@api_view(['GET'])
def get_team_hierarchy(request):
    def build_hierarchy(emp):
        return {
            "name": f"{emp.user.first_name} {emp.user.last_name}",
            "title": emp.designation.designationName,
            "gender": "Female" if emp.gender == "F" else "Male",
            "children": [
                build_hierarchy(sub)
                for sub in emp.subordinates.all()
            ]
        }

   
    top_level_employees = Employee.objects.filter(reports_to__isnull=True)

    ceo_node = {
        "name": "Vivek",
        "title": "Chief Executive Officer",
        "gender": "Male",
        "children": [build_hierarchy(emp) for emp in top_level_employees]
    }

    return Response(ceo_node)
@api_view(["POST"])
def time_sheet_detail(request):
   session = WorkSession.objects.all()
   serializer = WorkSessionSerializer(session,many=True)
   return Response(serializer.data)


@api_view(["POST","GET",'DELETE'])
@permission_classes([IsAuthenticated])
def daily_log(request):
    if(request.data and request.method=='POST'):
        dataDict = request.data
        from_date = dataDict['fromDate']
        to_date = dataDict['toDate']
        dailylog = WorkSession.objects.filter(user=request.user,clock_in__date__gte=from_date,clock_in__date__lte=to_date)
        logs = WorkSessionSerializer(dailylog,many=True)
        return Response({"dailyLog":logs.data})
    if request.method =='GET':
        dailylog = WorkSession.objects.filter(user=request.user)
        logs = WorkSessionSerializer(dailylog,many=True)
        return Response({"dailyLog":logs.data})
    return Response({"daily_log":"Expense Deleted"})

@api_view(['DELETE','PUT'])
@permission_classes([IsAuthenticated])
def delete_expense_daily_log(request,session_id,expense_id):
    if request.method =='DELETE':
        dailylog = TimeSheetDetails.objects.filter(id=expense_id).delete()
        print(dailylog)
        return Response({"daily_log":"Expense Deleted"},status=status.HTTP_200_OK)
    elif request.method =='PUT':
        expId = request.data.get('id')
        timeSheet = TimeSheetDetails.objects.get(id=expId)
        timeSheet.hourSpent = request.data.get('hourSpent')
        timeSheet.description = request.data.get('description')
        serializedTimeSheet = TimeSheetDetailsSerializer(timeSheet)
        timeSheet.save()
        print(serializedTimeSheet.data)
        return Response(serializedTimeSheet.data,status=status.HTTP_200_OK)

    else :
        return Response({"Error":"Unable to delete slot"},status=status.HTTP_400_BAD_REQUEST)
    

@api_view(["POST"])
def add_time_expense(request):
    try:
        session = request.data
        print(session['session_id'])
        sessionId = session['session_id']
        description = session['description']
        hourSpent = session['hourSpent']
        mySession = WorkSession.objects.get(id=sessionId)
        timeSheet = TimeSheetDetails.objects.create(session=mySession,hourSpent=hourSpent,description=description)
        serializedTimeSheet = TimeSheetDetailsSerializer(timeSheet)
        return Response(serializedTimeSheet.data)
    except:
         return Response({"error":'Unable to add details to daily log'},status=status.HTTP_400_BAD_REQUEST)
    

# submit_time_Sheet
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def submit_time_Sheet(request,sessionId):
    if request.method =='PUT':
        timeSheet = WorkSession.objects.get(id=sessionId)
        timeSheet.approval_status = 'Submitted'
        timeSheet.save()
        # print(timeSheet)
        return Response({"message":'Submit Time Sheet'},status=status.HTTP_200_OK)

    else :
        return Response({"Error":"Unable to submit"},status=status.HTTP_400_BAD_REQUEST)
