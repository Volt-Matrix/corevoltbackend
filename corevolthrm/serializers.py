from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from corevolthrm.models import Profiles, LeaveApplication, Employee, WorkSession,TimeSheetDetails,UploadDocument

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'password2', 'first_name', 'last_name', 'phone')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'phone': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user
    
class LeaveApplicationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = LeaveApplication
        fields = '__all__'
        read_only_fields = ['user']

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class ProfilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profiles
        fields = '__all__'
        extra_kwargs = {
            'employee': {'required': False},  # Allow view to set it manually
        }

class UploadDocumentSerializer(serializers.ModelSerializer):
    profile = serializers.PrimaryKeyRelatedField(queryset=Profiles.objects.all()) 

    class Meta:
        model = UploadDocument
        fields = '__all__'

    def validate(self, data):
        doc_type = data.get('doc_type')
        if doc_type == 'Education':
            if not data.get('degree'):
                raise serializers.ValidationError({'degree': 'Degree is required for education documents.'})
            if not data.get('institute'):
                raise serializers.ValidationError({'institute': 'Institute is required for education documents.'})
        elif doc_type == 'Experience':
            pass
        return data

class EmployeeSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()

    username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id',
            'employee_id',
            'gender',
            'employment_status',
            'birthday',
            'username',
            'user_email',
            'full_name',
            'email',
            'phone',
            'city',
            'country',
            'profile_picture',
        ]

    def get_full_name(self, obj):
        if obj.profile:
            return obj.profile.full_name
        return ''

    def get_email(self, obj):
        if obj.profile:
            return obj.profile.email
        return ''

    def get_phone(self, obj):
        if obj.profile:
            return obj.profile.phone
        return ''

    def get_city(self, obj):
        if obj.profile:
            return obj.profile.city
        return ''

    def get_country(self, obj):
        if obj.profile:
            return obj.profile.country
        return ''

    def get_profile_picture(self, obj):
        if obj.profile and obj.profile.profile_picture:
            request = self.context.get('request')
            url = obj.profile.profile_picture.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return ''

class TimeSheetDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSheetDetails
        fields = ['id', 'hourSpent', 'description']
class WorkSessionSerializer(serializers.ModelSerializer):
    timesheet_details = TimeSheetDetailsSerializer(many=True, read_only=True)
    class Meta:
        model = WorkSession
        fields = ['id','clock_in', 'clock_out','next_clock_in', 'total_work_time','approval_status','timesheet_details',]
class LeaveRequestSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
 
    class Meta:
        model = LeaveApplication
        fields = '__all__'
