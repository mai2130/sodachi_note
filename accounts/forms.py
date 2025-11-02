from django import forms
from django.contrib.auth import authenticate, get_user_model #認証処理・ユーザ取得
from django.core.exceptions import ValidationError

User = get_user_model()

class EmailAuthenticationForm(forms.Form):
    email = forms.EmailField(label='メールアドレス')
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput)
       
    def clean(self):
        cleaned = super().clean()
        email = cleaned.get('email')
        password = cleaned.get('password')
        if not email or not password:
            return cleaned
        try:
            user = User.objects.get(email=email) #入力メールに一致するユーザーをDBから1件取得
        except User.DoesNotExist:
            raise ValidationError('メールアドレスまたはパスワードが正しくありません')
        
        
        user = authenticate(username=user.username, password=password)
        if user is None:
            raise ValidationError('メールアドレスまたはパスワードが正しくありません')
        if not user.is_active: #退園の場合
            raise ValidationError('このアカウントは無効です')
        cleaned['user'] = user
        return cleaned
    
class FacilitySignUpForm(forms.Form):
    nursery_name = forms.CharField(label= "施設名", max_length=100)
    postal_code = forms.CharField(label ="郵便番号", max_length=8)
    address = forms.CharField(label = "住所", max_length=100)
    phone_number = forms.CharField(label = "電話番号", max_length=15)
    email = forms.EmailField(label = "メールアドレス")
    password1 = forms.CharField(label = "パスワード ※英数字８文字以上",widget=forms.PasswordInput)
    password2 = forms.CharField(label = "パスワード（確認用）",widget=forms.PasswordInput)
    
        
    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1")!= cleaned.get("password2"):
            raise ValidationError("パスワードが一致しません")
        if User.objects.filter(email=cleaned.get("email")).exists():
            raise ValidationError("このメールアドレスは既に使われています")
        return cleaned
        
                                                     
            