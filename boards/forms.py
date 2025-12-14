from django import forms
from .models import Board

class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ["date", "title", "category"]
        widgets = {
            "date":forms.DateInput(
                attrs={"type":"date", "placeholder":"20YY/MM/DD"}
            ),
            "title" : forms.TextInput(attrs={"class": "text-input"}),
            "category" :forms.Select(attrs={"class": "select-input"}),
        }
        