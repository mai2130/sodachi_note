from django import forms
from .models import Notice
from nurseries.models import Classroom

class NoticeForm(forms.ModelForm):
    classrooms = forms.ModelMultipleChoiceField( #クラスを複数選択可能にする
        queryset=Classroom.objects.all(),
        widget=forms.SelectMultiple(attrs={"class":"select-input"}),
        required=False,
        label="クラス名",
    )
    
    class Meta:
        model = Notice
        fields = ['date','title','category', 'classrooms', 'body','file']
        widgets = {
            'date' : forms.DateInput(attrs={'type': 'date'}),
            'title' : forms.TextInput(attrs={'class': 'text-input'}),
            'category' : forms.Select(attrs={'class': 'select-input'}),
            'body' : forms.Textarea(attrs={
                'rows': 6, #行数
                'class': 'textarea-input', 
                'placeholder': '本文'
            }),
        }