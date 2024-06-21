from django import forms
from .models import task

class createform(forms.ModelForm):
    class Meta:
        model = task
        fields = ['name', 'descrption', 'status']