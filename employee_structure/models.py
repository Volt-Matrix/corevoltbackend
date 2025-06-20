from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from corevolthrm.models import Employee
# Create your models here.
User = get_user_model()

class Project(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    managers = models.ManyToManyField(
        Employee,
        related_name='managed_projects',
        blank=True,
        help_text="Employees who are managers of this project."
    )
    members = models.ManyToManyField(
        Employee,
        related_name='projects',
        blank=True,
        help_text="Employees who are members of this project."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return self.name
