from django.db import models
from django.utils import timezone

class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)  # Optional: Allow empty descriptions
    due_date = models.DateField(null=True, blank=True)  # Optional: Allow no due date
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('IN_PROGRESS', 'In Progress'),
            ('COMPLETED', 'Completed'),
        ],
        default='PENDING'
    )
    created_at = models.DateTimeField(auto_now_add=True)  # Optional: Track creation time
    updated_at = models.DateTimeField(auto_now=True)  # Optional: Track updates

    def __str__(self):
        return self.title

