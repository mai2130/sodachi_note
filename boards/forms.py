from django import forms
from django.utils import timezone
from .models import Board

class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ["date", "title", "category"]
        widgets = {
            "date":forms.DateInput(
                attrs={"type":"date", "class":"text-input",}
            ),
            "title" : forms.TextInput(attrs={"class": "text-input"}),
            "category" :forms.Select(attrs={"class": "select-input"}),
        }
        error_messages = {
            "title": {
                "required": "タイトルを入力してください",
                "max_length": "タイトルは100文字以内で入力してください",
            },
            "category": {
                "required": "カテゴリを選択してください",
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        category_choices = [
            choice for choice in self.fields["category"].choices
            if choice[0] != ""
        ]
        self.fields["category"].choices = [("", "カテゴリ")] + category_choices

        if not self.instance.pk:
            self.fields["date"].initial = timezone.localdate()

        self.fields["date"].disabled = True