# tasks/forms.py

from django import forms
from django.utils import timezone
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "due_date", "completed"]  # Zmenené z "status" na "completed"
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Zadajte názov úlohy...',
                'maxlength': 100
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Voliteľný popis úlohy...',
                'rows': 4
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'completed': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def clean_due_date(self):
        due = self.cleaned_data.get("due_date")
        if due and due < timezone.now().date():
            raise forms.ValidationError("Due date cannot be in the past.")
        return due