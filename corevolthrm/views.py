from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import UserRegistrationSerializer,EmployeeSerializer
from django.contrib.auth import authenticate,login
from django.views.decorators.http import require_POST,require_GET
from django.middleware.csrf import get_token
from rest_framework.decorators import api_view,permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from corevolthrm.models import Employee

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
                    'role':role
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
    response = JsonResponse({"message": "Logout successful",'isLogged':False})
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response


@api_view(["GET"])
def AddEmployee(request):
    return JsonResponse({'message':"request received"})
