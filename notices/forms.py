from django import forms
from django.utils import timezone
from .models import Notice
from nurseries.models import Classroom

class NoticeForm(forms.ModelForm):
    classroom = forms.ModelChoiceField( 
        queryset=Classroom.objects.none(),
        required=False,
        label="クラス名",
        empty_label="全園児",
        widget=forms.Select(attrs={"class": "select-input"}),
    )
    
    def __init__(self, *args, nursery=None, **kwargs):
        super().__init__(*args, **kwargs)
        if nursery:
            self.fields["classroom"].queryset = Classroom.objects.filter(nursery=nursery)

        if self.instance and self.instance.pk:
            first = self.instance.classrooms.first()
            self.fields["classroom"].initial = first

        else:
            self.fields["date"].initial = timezone.localdate()

        self.fields["title"].error_messages = {
            "required": "タイトルを入力してください"
        }
        self.fields["body"].error_messages = {
            "required": "本文を入力してください"
        }  
    class Meta:
        model = Notice
        fields = ['date','title','category', 'classroom', 'body','file']
        widgets = {
            'date' : forms.DateInput(attrs={'type': 'date', 'class' : 'text-input'}),
            'title' : forms.TextInput(attrs={'class': 'text-input'}),
            'category' : forms.Select(attrs={'class': 'select-input'}),
            'body' : forms.Textarea(attrs={
                'rows': 6, #行数
                'class': 'textarea-input', 
                'placeholder': '本文'
            }),
        }