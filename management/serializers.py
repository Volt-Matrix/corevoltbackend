
from rest_framework import serializers
from corevolthrm.models import TeamName,User
from management.models import ProjectDetail

class UserNameSerialzier(serializers.ModelSerializer):
    class Meta:
        model = User
        fields=['first_name']

class TeamNameSerializer(serializers.ModelSerializer):
    """Serializer for TeamName model"""
    class Meta:
        model = TeamName
        fields = ['id', 'name', 'active', 'total_members']

class ProjectDetailSerializer(serializers.ModelSerializer):
    """Serializer for ProjectDetail with teams list"""
    teams = TeamNameSerializer(many=True, read_only=True)
    project_leader = UserNameSerialzier()
    class Meta:
        model = ProjectDetail
        fields = ['id', 'project_name', 'teams', 'is_active', 'created_date','project_leader']