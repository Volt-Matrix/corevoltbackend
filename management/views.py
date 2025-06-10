from django.shortcuts import render
from corevolthrm.models import TeamName
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from .serializers import ProjectDetailSerializer
from management.models import ProjectDetail
# Create your views here.
User = get_user_model()

class Management(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        projectId = request.GET.get('projectId')
        if projectId:
            projects = ProjectDetail.objects.get(id=projectId)
            projectDetail = ProjectDetailSerializer(projects)
            return Response(projectDetail.data,status=status.HTTP_200_OK)
        projects = ProjectDetail.objects.all()
        projectDetail = ProjectDetailSerializer(projects,many=True)
        return Response(projectDetail.data, status=status.HTTP_200_OK)
    
    def post(self,request):
        return Response({"Message":"Create Project view"},status=status.HTTP_200_OK)
