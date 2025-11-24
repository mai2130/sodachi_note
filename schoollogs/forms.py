from datetime import time
from django import forms
from .models import SchoolGrowthLog

def ten_minute_choices():
    choices = []
    for h in range(24):
        for m in range(0,60,10):
            t = time(hour=h, minute=m)
            label = t.strftime("%H:%M")
            choices.append((label,label))
    return choices

class SchoolGrowthLogForm(forms.ModelForm):
    class Meta:
        model = SchoolGrowthLog
        fields = [
            'child',
            'date',
            'lunch',
            'nap_start',
            'nap_end',
            'poo',
            'condition',
            'temperature',
            'state',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'nap_start': forms.TimeInput(attrs={'type': 'time', 'step': 600}), #10分単位
            'nap_end': forms.TimeInput(attrs={'type': 'time', 'step': 600}), #10分単位           
            'state': forms.Textarea(attrs={'rows': 4}),
            'poo': forms.RadioSelect(),
            'lunch': forms.RadioSelect(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        
        self.fields["nap_start"].widget = forms.Select(choices=ten_minute_choices())
        self.fields["nap_end"].widget = forms.Select(choices=ten_minute_choices())
        