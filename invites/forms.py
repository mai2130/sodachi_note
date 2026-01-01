from django import forms
from children.models import Child
from datetime import date

def month_choices(years=3): # 現在月から指定年数(3年）分の選択肢を作成
    today = date.today()
    choices = [('', '20YY/MM')]
    y = today.year
    m = today.month
    
    for i in range(years * 12): # 月数分ループ
        yy = y + (m + i - 1) // 12 # 年をまたぐ場合の調整
        mm = (m + i - 1) % 12 + 1 # 1～12月に収める調整
        value = f"{yy}-{mm:02d}-01" #DB保存用
        label = f"{yy}/{mm:02d}" #画面表示用
        choices.append((value, label))
    return choices

class AccountManageForm(forms.ModelForm):
    withdrawn_month = forms.ChoiceField(
        choices=month_choices(),
        required=False,
        widget=forms.Select(attrs={"class": "mypage-input"}),
    )
    
    class Meta:
        model = Child
        fields = ["name", "classroom", "withdrawn_month"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "mypage-input"}),
            "classroom": forms.Select(attrs={"class": "mypage-input"}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 既存値がある場合、初期選択を合わせる
        if self.instance and getattr(self.instance, "withdrawn_month", None):
            self.fields["withdrawn_month"].initial = self.instance.withdrawn_month.strftime("%Y-%m-01")

    def clean_withdrawn_month(self):
        value = self.cleaned_data.get("withdrawn_month")
        if not value:
            return None
        y, m, _ = map(int, value.split("-"))
        return date(y, m, 1)


