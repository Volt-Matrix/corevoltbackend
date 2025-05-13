from django.shortcuts import render
from django.http import JsonResponse
# Create your views here.
def profile_list(request):
    if request.method == 'GET':
        return JsonResponse({"message":"Request recived"})