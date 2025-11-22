from django import forms
from .models import SchoolGrowthLog

class SchoolGrowthLogForm(forms.ModelForm):
    class Meta:
        model = SchoolGrowthLog
        fields = [
            'child',
            'date',
            'lunch',
            'nap_time',
            'poo',
            'condition',
            'temperature',
            'state',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'nap_time': forms.TimeInput(attrs={'type': 'time'}),
            'state': forms.Textarea(attrs={'rows': 4}),
            'poo': forms.RadioSelect(),
            'lunch': forms.RadioSelect(),
        }
        