from datetime import time
from django import forms
from .models import GrowthLog

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
        model = GrowthLog
        fields = [
            'school_lunch',
            'school_nap_start',
            'school_nap_end',
            'school_poo',
            'school_condition',
            'school_temperature',
            'school_state',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'school_nap_start': forms.TimeInput(attrs={'type': 'time', 'step': 600}), #10分単位
            'school_nap_end': forms.TimeInput(attrs={'type': 'time', 'step': 600}), #10分単位           
            'school_state': forms.Textarea(attrs={'rows': 4}),
            'school_poo': forms.RadioSelect(),
            'school_lunch': forms.RadioSelect(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
                
        self.fields["school_nap_start"].widget = forms.Select(choices=ten_minute_choices())
        self.fields["school_nap_end"].widget = forms.Select(choices=ten_minute_choices())

class HomeGrowthLogForm(forms.ModelForm):
    home_bedtime = forms.ChoiceField(
        choices=ten_minute_choices(),
        required=False,
        label="就寝時間"
    )
    home_wake_up_time = forms.ChoiceField(
        choices=ten_minute_choices(),
        required=False,
        label="起床時間"
    )

    class Meta:
        model = GrowthLog
        fields = [
            "home_bedtime",
            "home_wake_up_time",
            "home_appetite",
            "home_condition",
            "home_temperature",
            "home_poo",
            "home_state",
        ]
        widgets = {
            "home_appetite": forms.RadioSelect(),
            "home_condition": forms.Select,
            "home_poo": forms.RadioSelect(),
            "home_state": forms.Textarea(attrs={"rows": 4}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.home_bedtime:
            self.initial["home_bedtime"] = self.instance.home_bedtime.strftime("%H:%M")
        if self.instance and self.instance.home_wake_up_time:
            self.initial["home_wake_up_time"] = self.instance.home_wake_up_time.strftime("%H:%M")
            
        if self.instance and getattr(self.instance, "submitted", False):
            for f in self.fields.values():
                f.disabled = True

    def _clean_time(self, v):
        if not v:
            return None
        h, m = map(int, v.split(":"))
        return time(h, m)

    def clean_home_bedtime(self):
        return self._clean_time(self.cleaned_data.get("home_bedtime"))

    def clean_home_wake_up_time(self):
        return self._clean_time(self.cleaned_data.get("home_wake_up_time"))
