from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from employee_structure.models import Project
from corevolthrm.models import Employee, Role, TeamName
from employee_structure.serializers import ProjectSerializer, RoleSerializer, EmployeeWithRoleSerializer, TeamNameSerializer, BasicEmployeeSerializer
from corevolthrm.customPermission.customPermissionClasss import IsManagerOrAdmin

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().prefetch_related('managers', 'members')
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsManagerOrAdmin]

    @action(detail=True, methods=['post'], url_path='add-member')
    def add_member(self, request, pk=None):
        project = self.get_object()
        employee_id = request.data.get('employee_id')
        if not employee_id:
            return Response({'error': 'employee_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            employee = Employee.objects.get(id=employee_id)
            project.members.add(employee)
            return Response({'status': 'member added'}, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], url_path='remove-member')
    def remove_member(self, request, pk=None):
        project = self.get_object()
        employee_id = request.data.get('employee_id')
        if not employee_id:
            return Response({'error': 'employee_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            employee = Employee.objects.get(id=employee_id)
            project.members.remove(employee)
            return Response({'status': 'member removed'}, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], url_path='add-manager')
    def add_manager(self, request, pk=None):
        project = self.get_object()
        employee_id = request.data.get('employee_id')
        if not employee_id:
            return Response({'error': 'employee_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            employee = Employee.objects.get(id=employee_id)
            project.managers.add(employee)
            return Response({'status': 'manager added'}, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], url_path='remove-manager')
    def remove_manager(self, request, pk=None):
        project = self.get_object()
        employee_id = request.data.get('employee_id')
        if not employee_id:
            return Response({'error': 'employee_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            employee = Employee.objects.get(id=employee_id)
            project.managers.remove(employee)
            return Response({'status': 'manager removed'}, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)


class TeamViewSet(viewsets.ModelViewSet):
    queryset = TeamName.objects.all().prefetch_related('manager__user', 'members__user')
    serializer_class = TeamNameSerializer
    permission_classes = [IsAuthenticated, IsManagerOrAdmin]

    # Action to update manager
    @action(detail=True, methods=['post'], url_path='set-manager')
    def set_manager(self, request, pk=None):
        team = self.get_object()
        manager_id = request.data.get('employee_id')
        if manager_id is None: # Allow unsetting manager
            team.manager = None
            team.save()
            return Response({'status': 'manager removed'}, status=status.HTTP_200_OK)
        try:
            new_manager = Employee.objects.get(id=manager_id)
            team.manager = new_manager
            team.save()
            return Response(TeamNameSerializer(team).data, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee (manager) not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], url_path='add-member')
    def add_member(self, request, pk=None):
        team = self.get_object()
        employee_id = request.data.get('employee_id')
        if not employee_id:
            return Response({'error': 'employee_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            employee = Employee.objects.get(id=employee_id)
            team.members.add(employee)
            # Optionally, update the employee's primary team
            # employee.team = team
            # employee.save()
            return Response({'status': 'member added to team'}, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], url_path='remove-member')
    def remove_member(self, request, pk=None):
        team = self.get_object()
        employee_id = request.data.get('employee_id')
        if not employee_id:
            return Response({'error': 'employee_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            employee = Employee.objects.get(id=employee_id)
            team.members.remove(employee)
            # Optionally, if this was their primary team, nullify it or reassign
            # if employee.team == team:
            #     employee.team = None
            #     employee.save()
            return Response({'status': 'member removed from team'}, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)


class RoleListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrAdmin]
    def get(self, request):
        roles = Role.objects.filter(is_active=True)
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)

class EmployeeRoleListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrAdmin]
    def get(self, request):
        employees = Employee.objects.select_related('user', 'role').all()
        serializer = EmployeeWithRoleSerializer(employees, many=True)
        return Response(serializer.data)

class EmployeeRoleUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrAdmin]
    def patch(self, request, employee_id):
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)

        role_id = request.data.get('role_id')
        if not role_id:
            return Response({'error': 'role_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_role = Role.objects.get(id=role_id)
            employee.role = new_role
            employee.save()
            serializer = EmployeeWithRoleSerializer(employee)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Role.DoesNotExist:
            return Response({'error': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Endpoint to get a list of all employees (basic info) for selection dropdowns
class AllEmployeesListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrAdmin]
    def get(self, request):
        employees = Employee.objects.select_related('user').all()
        serializer = BasicEmployeeSerializer(employees, many=True)
        return Response(serializer.data)