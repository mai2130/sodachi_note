from django import forms
from django.contrib.auth import authenticate, get_user_model #認証処理・ユーザ取得
from django.core.exceptions import ValidationError

from invites.models import InviteCode
from families.models import Family

User = get_user_model()

# メール＋パスワードでログインできるかチェック、ログイン対象ユーザーを返す
class EmailAuthenticationForm(forms.Form):
    email = forms.EmailField(label='メールアドレス')
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput)
    
    # フォーム全体の整合性チェック   
    def clean(self):
        cleaned = super().clean()
        email = cleaned.get('email')
        password = cleaned.get('password')
        if not email or not password:
            return cleaned
        try:
            user = User.objects.get(email=email) # 入力メールに一致するユーザーをDBから1件取得
        except User.DoesNotExist:
            raise ValidationError('メールアドレスまたはパスワードが正しくありません')
        
        user = authenticate(username=user.username, password=password)
        if user is None:
            raise ValidationError('メールアドレスまたはパスワードが正しくありません')
        if not user.is_active: # 退園時
            raise ValidationError('このアカウントは無効です')
        cleaned['user'] = user
        return cleaned

# 施設（園）側の新規登録フォーム    
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

# 保護者側の新規登録フォーム
class GuardianSignUpForm(forms.Form):
    invite_code = forms.CharField(label="認証コード", max_length=6)
    child_name = forms.CharField(label="園児氏名", max_length=50)
    guardian_name = forms.CharField(label="保護者氏名", max_length=30)
    relationship = forms.ChoiceField(choices=[("","")] + list(Family.Relationship.choices), label="続柄")
    email = forms.EmailField(label="メールアドレス")
    password1 = forms.CharField(label="パスワード ※英数字８文字以上", widget=forms.PasswordInput)
    password2 = forms.CharField(label="パスワード（確認用）", widget=forms.PasswordInput)
    
    def clean_invite_code(self):
        code = (self.cleaned_data.get("invite_code") or "").strip().upper() # strip()：前後スペース削除, upper()：小文字で入れても大文字扱いにする（例: ab12cd → AB12CD）
        try:
            invite = InviteCode.objects.select_related("child").get(short_code=code)
        except (InviteCode.DoesNotExist, ValueError , TypeError):
            raise ValidationError("認証コードが正しくありません")
        
        if not invite.is_available:
            raise ValidationError("この認証コードは利用上限に達しています")
    
        self.cleaned_data['invite'] = invite
        return code
    
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("このメールアドレスは既に使われています")
        return email
        
    def clean(self):
        cleaned = super().clean()
    #パスワード一致確認
        if cleaned.get("password1") != cleaned.get("password2"):
            self.add_error("password2", "パスワードが一致しません")

    #園児名確認
        invite =cleaned.get("invite")
        child_name = cleaned.get("child_name")
    
        if invite and child_name and invite.child.name != child_name:
            self.add_error("child_name", "園児氏名が認証コードと一致しません")

        return cleaned                      