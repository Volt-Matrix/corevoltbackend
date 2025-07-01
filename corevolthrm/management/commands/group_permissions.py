from django.core.management.base import BaseCommand
from datetime import datetime
from django.contrib.auth.models import Group,Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Create User Groups and permissions'

    def add_arguments(self, parser):
        # parser.add_argument('group_permission', type = str, help = '')
        return

    def handle(self, *args, **options):
        # Create Group-------------
        # employee_group = Group.objects.get_or_create(name="employee")
        # Create Permisssion
        # Add permission to group
        # Add users to group----------
        # rav = rav.groups.add(employee_group)
        # print('Running command to setup groups and permissions')
        User = get_user_model()
        print('Groups and permission')
        # rav = User.objects.get(email='kotesh@gmail.com')
        # print(rav)
        # userCTtype = ContentType.objects.get_for_model(User)
        # grp,employee_group = Group.objects.get_or_create(name="employee")
        # manager_group = Group.objects.get_or_create(name="manager")
        # hradmin_group = Group.objects.get_or_create(name="hradmin")
        # rav = rav.groups.add(employee_group)
        # print(rav)
        myCustomPermissions = [('role_can_view_','Can view resource'),('role_can_create','Create a resource'),('role_can_delete','Can delete resource'),('role_can_edit','Role can edit resource')]
        # permission = Permission.objects.get(codename='cam_delete_expense')
        # for codeName,name in myCustomPermissions:
        #     permission, created = Permission.objects.get_or_create(
        #         codename=codeName,
        #         name=name,
        #         content_type=userCTtype,
        #         )
        #     grp.permissions.add(permission)

        
