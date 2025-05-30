from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import UserRegistrationSerializer,LeaveApplicationSerializer
from django.contrib.auth import authenticate,login
from django.views.decorators.http import require_POST,require_GET
from django.middleware.csrf import get_token
from rest_framework.decorators import api_view,permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

from rest_framework import viewsets

from corevolthrm.models import Announcement
from corevolthrm.serializers import AnnouncementSerializer
from rest_framework.permissions import IsAdminUser
from .models import LeaveRequest
from .serializers import LeaveRequestSerializer
from corevolthrm.models import LeaveApplication
from django.contrib.auth import get_user_model
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
        else:
            print("Serializer error:",serializer.errors)
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@require_POST
def loginUser(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        data = json.loads(request.body)
        email = data.get('userName')
        password = data.get('password')
        user = authenticate(request, email=email, password=password)
        
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
                },
                "csrf_token": csrf_token,  # Include CSRF token in response for frontend
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
                max_age=15 * 60
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
            max_age=15 * 60  # 15 minutes
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
   
def logoutUser(request):
    response = JsonResponse({"message": "Logout successful"})
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response

class AnnouncementList(generics.ListCreateAPIView):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated]
    
# GET all leave requests (admin)
class LeaveRequestListAPIView(generics.ListCreateAPIView):
    queryset = LeaveApplication.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]
    print(queryset)
    
class UpdateLeaveStatusAPIView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
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

@api_view(['GET'])
def total_users_count(request):
    User = get_user_model()
    total_users = User.objects.count()
    return Response({"total_users": total_users})