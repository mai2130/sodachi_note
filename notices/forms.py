from django import forms
from django.utils import timezone
from .models import Notice
from nurseries.models import Classroom

class NoticeForm(forms.ModelForm):
    classroom = forms.ModelChoiceField( 
        queryset=Classroom.objects.all(),
        required=False,
        label="クラス名",
        empty_label="全園児",
        widget=forms.Select(attrs={"class": "select-input"}),
    )
    
    def __init__(self, *args,  **kwargs):
        super().__init__(*args, **kwargs)
        
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

    def clean(self):
        cleaned_data = super().clean()

        date = cleaned_data.get('date')
        title = cleaned_data.get('title')
        classroom = cleaned_data.get('classroom')
        
        if not  date or not title:
            return cleaned_data
        
        qs = Notice.objects.filter(date=date, title=title,)

        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if classroom:
            qs = qs.filter(classrooms=classroom)
        else:
            qs = qs.filter(classrooms__isnull=True)

        if qs.exists():
            raise forms.ValidationError("同じ日付、タイトル、クラスのおしらせが既に存在しています")

        return cleaned_data
            
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