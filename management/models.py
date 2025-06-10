from django.db import models
from datetime import date
from django.contrib.auth import get_user_model

# Create your models here.
User = get_user_model()

class ProjectDetail(models.Model):
    project_name = models.CharField(max_length=30,unique=True)
    teams = models.ManyToManyField('corevolthrm.TeamName',related_name='projects',blank=True,null=True)
    is_active = models.BooleanField(default=True)
    created_date = models.DateField(default=date.today)
    project_leader = models.ForeignKey(User, on_delete=models.CASCADE,blank=True,null=True)
    class Meta:
        ordering = ['project_name']
    def __str__(self):
        return self.project_name