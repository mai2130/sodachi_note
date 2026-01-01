from django import forms
from .models import Nursery

class NurseryMyPageForm(forms.ModelForm):
    class Meta:
        model =Nursery
        fields = ["name", "postal_code", "address", "phone_number"] 
        widgets = {
            "name": forms.TextInput(attrs={"class": "mypage-input"}),
            "postal_code": forms.TextInput(attrs={"class": "mypage-input"}),
            "address": forms.TextInput(attrs={"class": "mypage-input"}),
            "phone_number": forms.TextInput(attrs={"class": "mypage-input"}),
        }