from django.db import models

# Create your models here.
class Announcement(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=False)
    content = models.TextField()

    class Meta:
        ordering = ['-created']

class Holiday(models.Model):
    name = models.CharField(max_length = 30, blank=False)
    date = models.DateField()

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ['date']