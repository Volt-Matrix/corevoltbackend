from rest_framework import serializers
from employee_structure.models import Project
from corevolthrm.models import Employee, Role, TeamName

class BasicEmployeeSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ['id', 'employee_id', 'full_name']

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}" if obj.user else obj.employee_id


class ProjectSerializer(serializers.ModelSerializer):
    managers = BasicEmployeeSerializer(many=True, read_only=True)
    members = BasicEmployeeSerializer(many=True, read_only=True)
    manager_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Employee.objects.all(), source='managers', write_only=True, required=False
    )
    member_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Employee.objects.all(), source='members', write_only=True, required=False
    )

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'managers', 'members', 'manager_ids', 'member_ids', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    # If you want to allow creating/updating managers/members by ID list directly:
    # def create(self, validated_data):
    #     manager_ids = validated_data.pop('manager_ids', [])
    #     member_ids = validated_data.pop('member_ids', [])
    #     project = Project.objects.create(**validated_data)
    #     if manager_ids:
    #         project.managers.set(manager_ids)
    #     if member_ids:
    #         project.members.set(member_ids)
    #     return project

    # def update(self, instance, validated_data):
    #     manager_ids = validated_data.pop('manager_ids', None)
    #     member_ids = validated_data.pop('member_ids', None)
        
    #     instance = super().update(instance, validated_data)

    #     if manager_ids is not None:
    #         instance.managers.set(manager_ids)
    #     if member_ids is not None:
    #         instance.members.set(member_ids)
    #     return instance


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'get_name_display', 'description'] # get_name_display gives the human-readable name


# Employee Serializer for Role Management context
class EmployeeWithRoleSerializer(serializers.ModelSerializer):
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    role_name = serializers.CharField(source='role.get_name_display', read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), source='role', write_only=True)

    class Meta:
        model = Employee
        fields = ['id', 'employee_id', 'user_full_name', 'user_email', 'role', 'role_name', 'role_id']
        read_only_fields = ['employee_id', 'user_full_name', 'user_email', 'role_name']
        extra_kwargs = {
            'role': {'read_only': True}
                                        
        }

class TeamNameSerializer(serializers.ModelSerializer):
    manager = BasicEmployeeSerializer(read_only=True)
    members = BasicEmployeeSerializer(many=True, read_only=True)
    manager_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(), source='manager', write_only=True, required=False, allow_null=True
    )
    member_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Employee.objects.all(), source='members', write_only=True, required=False
    )
    calculated_total_members = serializers.SerializerMethodField()

    class Meta:
        model = TeamName
        fields = ['id', 'name', 'active', 'manager', 'members', 'manager_id', 'member_ids', 'calculated_total_members']
    
    def get_calculated_total_members(self, obj):
        return obj.members.count()