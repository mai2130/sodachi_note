from django import forms
from .models import Nursery

class NurseryForm(forms.form):
    class Meta:
        model =Nursery
        fields = ["name", "postal_code", "address", "phone_number","email"]