from django import forms
from django.contrib.auth import authenticate, get_user_model #認証処理・ユーザ取得
from django.contrib.auth.forms import PasswordChangeForm 
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
    
    def save(self):
        invite = self.clened_data["invite"]
        child = invite.child

        full_name = (self.cleaned_data.get("guardian_name") or "").strip()
        parts = full_name.split()

        if len(parts) >= 2:
            last_name = parts[0]
            first_name = "".join(parts[1:])
        elif len(parts) == 1:
            last_name = parts[0]
            first_name = ""
        else:
            last_name = ""
            first_name = ""

        email = self.cleaned_data["email"]
        password = self.cleaned_data["password1"]
        relationship = self.cleaned_data.get("relationship")

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            last_name=last_name,
            first_name=first_name,
            role=User.Role.GUARDIAN,
            relationship=relationship if relationship != "" else None,
            active_child=child,
        )

        Family.objects.create(
            user=user,
            child=child,
            relationship=relationship if relationship != "" else None,
        )

        invite.users_count += 1
        invite.save(update_fields=["users_count"])

        return user

# マイページ管理画面（園児用）
class ChildMyPageForm(forms.ModelForm):

    guardian_name = forms.CharField(required=False, label="保護者氏名")
    class Meta:
        model = User
        fields = ["relationship", "email", "postal_code", "address", "phone_number"]
        labels = {
            "relationship" : "続柄", 
            "email" : "メールアドレス",
            "postal_code" : "郵便番号",
            "address" : "住所",
            "phone_number" : "電話番号",
        } 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["relationship"].choices = [
            (0,"父"),
            (1,"母"),
            (2,"祖父"),
            (3,"祖母"),
            (4,"その他"),
        ]

        last_name = self.instance.last_name or ""
        first_name = self.instance.first_name or ""
        full = f"{last_name} {first_name}".strip()
        self.fields["guardian_name"].initial = full

    def clean_guardian_name(self):
        return (self.cleaned_data.get("guardian_name") or "").strip()
    
    def save(self, commit=True):
        user = super().save(commit=False)

        full = (self.cleaned_data.get("guardian_name") or "").strip()
        full = full.replace("  ","  ")

        if full:
            parts = full.split()

            if len(parts) >= 2 :
                user.last_name  = parts[0]
                user.first_name = " ".join(parts[1:])
            elif len(parts) == 1:
                user.last_name = parts[0]
                user.first_name = ""
            else:
                user.last_name = ""
                user.first_name = ""

        if commit:
            user.save()
        
        return user

class UserPasswordChangeForm(PasswordChangeForm):
    error_messages = PasswordChangeForm.error_messages.copy()
    error_messages.update({
        "password_incorrect": "現在のパスワードが正しくありません",
        "password_mismatch": "新しいパスワードと確認用パスワードが一致しません",    
    })

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ラベル名
        self.fields["old_password"].label = "現在のパスワード"
        self.fields["new_password1"].label = "新しいパスワード"
        self.fields["new_password2"].label = "新しいパスワード（確認用）"

        # 必須エラー文
        self.fields["old_password"].error_messages["required"] = "現在のパスワードを入力してください"
        self.fields["new_password1"].error_messages["required"] = "新しいパスワードを入力してください"
        self.fields["new_password2"].error_messages["required"] = "確認用パスワードを入力してください"

        # help_text を消したい場合
        self.fields["old_password"].help_text = ""
        self.fields["new_password1"].help_text = ""
        self.fields["new_password2"].help_text = ""

    def clean(self):
        cleaned_data = super().clean()

        old_password = cleaned_data.get("old_password")
        new_password1 = cleaned_data.get("new_password1")

        # 現在と同じパスワードを禁止
        if old_password and new_password1 and old_password == new_password1:
            self.add_error("new_password1", "現在と同じパスワードは設定できません")

        return cleaned_data