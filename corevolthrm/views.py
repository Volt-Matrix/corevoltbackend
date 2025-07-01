from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserRegistrationSerializer, LeaveApplicationSerializer,EmployeeSerializer,WorkSessionSerializer,LeaveRequestSerializer,TimeSheetDetailsSerializer
from django.contrib.auth import authenticate,get_user_model
from django.views.decorators.http import require_POST
from django.middleware.csrf import get_token
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from corevolthrm.models import LeaveApplication,Employee,WorkSession,LeaveApplication,LeaveRequest,TimeSheetDetails
from datetime import timedelta
from django.utils import timezone
from django.core import serializers
from .models import Profiles
from .serializers import ProfilesSerializer

from rest_framework import viewsets, permissions
from .models import AssetRequest
from .serializers import AssetRequestSerializer
from datetime import date
from .models import AssetCategory, Asset
from .serializers import AssetCategorySerializer, AssetSerializer
from .models import AssetList
from .serializers import AssetListSerializer
from .models import Employee
from .serializers import AssignedEmployeeSerializer,MyAssetListSerializer 


from rest_framework.authentication import SessionAuthentication
 
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

    def get(self, request):
        profiles = Profiles.objects.all()
        serializer = ProfilesSerializer(profiles, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProfilesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfilesDetailView(APIView):
    parser_classes = (JSONParser, MultiPartParser, FormParser) 

    def get(self, request, pk):
        try:
            profile = Profiles.objects.get(pk=pk)
        except Profiles.sDoesNotExist:
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
        return Response(status=status.HTTP_204_NO_CONTENT)
    
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
    session = WorkSession.objects.filter(user=request.user, clock_out__isnull=True).first()
    if session:
        session.clock_out = timezone.now()
        # Calculate total work time excluding breaks
        total_time = session.clock_out - session.clock_in
        total_breaks = session.total_break_time()
        session.total_work_time = total_time - total_breaks

        session.save()
        return Response({'Message':"Successfully clocked out"},status=status.HTTP_200_OK)

class LeaveRequestListAPIView(generics.ListCreateAPIView):
    queryset = LeaveApplication.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]
   
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
        dailylog = WorkSession.objects.filter(user=request.user,clock_in__range=(from_date,to_date))
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
    
class MyAssetsAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MyAssetListSerializer  

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'employee_profile'):
            return AssetList.objects.filter(assignedTo=user.employee_profile)
        return AssetList.objects.none()
class AssetRequestCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):  
        requests = AssetRequest.objects.all()
        serializer = AssetRequestSerializer(requests, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AssetRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateAssetRequestStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            asset_request = AssetRequest.objects.get(pk=pk)
            status_value = request.data.get("status")

            if status_value not in ["Approved", "Rejected"]:
                return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

           
            if status_value == "Rejected":
                asset_request.status = "Rejected"
                asset_request.save()
                serializer = AssetRequestSerializer(asset_request)
                return Response(serializer.data, status=200)

            
            already_approved = asset_request.status == "Approved"
            if status_value == "Approved" and not already_approved:
                try:
                    employee = asset_request.user.employee_profile
                except AttributeError:
                    return Response({"error": "User is not linked to Employee"}, status=400)

                asset = asset_request.asset_type
                if not asset:
                    return Response({"error": "No asset type found in this request"}, status=404)

                available_asset = AssetList.objects.filter(asset=asset, status="Available").first()
                if not available_asset:
                    return Response({"error": "Out of stock: No available assets"}, status=400)

                
                available_asset.status = "Assigned"
                available_asset.assignedTo = employee
                available_asset.assignedDate = date.today()
                available_asset.save()

                asset.update_total_and_available()

                
                asset_request.status = "Approved"
                asset_request.save()

            serializer = AssetRequestSerializer(asset_request)
            return Response(serializer.data, status=200)

        except AssetRequest.DoesNotExist:
            return Response({"error": "AssetRequest not found"}, status=404)


class AssetCategoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = AssetCategory.objects.all()
    serializer_class = AssetCategorySerializer


class AssetListCreateAPIView(generics.ListCreateAPIView):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer

class AssetRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer

class AssetListListCreateAPIView(generics.ListCreateAPIView):
    
    serializer_class = AssetListSerializer
    def get_queryset(self):
        status = self.request.query_params.get('status')
        if status:
            return AssetList.objects.filter(status=status)
        return AssetList.objects.all()


class AssetListRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AssetList.objects.all()
    serializer_class = AssetListSerializer

    


class AssetListListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AssetListSerializer

    def get_queryset(self):
        queryset = AssetList.objects.all()
        status = self.request.query_params.get('status')
        asset_id = self.request.query_params.get('asset')  

        if status:
            queryset = queryset.filter(status=status)
        if asset_id:
            queryset = queryset.filter(asset_id=asset_id)  
        return queryset
class AssetListByAssetView(generics.ListAPIView):
    serializer_class = AssetListSerializer

    def get_queryset(self):
        asset_id = self.kwargs['asset_id']
        return AssetList.objects.filter(asset_id=asset_id)

class EmployeeListView(generics.ListAPIView):
    queryset = Employee.objects.all()
    serializer_class = AssignedEmployeeSerializer
 