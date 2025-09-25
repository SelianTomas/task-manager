# tasks/forms.py

from django import forms
from django.utils import timezone
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "due_date", "status"]  # uprav podľa polí v tvojom modeli

    def clean_due_date(self):
        due = self.cleaned_data.get("due_date")
        if due and due < timezone.now().date():
            raise forms.ValidationError("Due date cannot be in the past.")
        return due
