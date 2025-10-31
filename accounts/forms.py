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
    
