from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "due_date", "completed")
    search_fields = ("title",)
    list_filter = ("completed", "due_date")