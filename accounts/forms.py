from django import forms
from django.contrib.auth import authenticate, get_user_model #認証処理・ユーザ取得
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm ,SetPasswordForm
from django.core.exceptions import ValidationError
import re

from invites.models import InviteCode
from families.models import Family

def validate_alnum_password(password):
    if len(password) < 8:
        raise ValidationError("パスワードは8文字以上で入力してください")
    if not re.search(r"[A-Za-z]", password):
        raise ValidationError("パスワードは英字を含めてください")
    if not re.search(r"[0-9]", password):
        raise ValidationError("パスワードは数字を含めてください")

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
    nursery_name = forms.CharField(label= "施設名", max_length=100,
                                   error_messages={"required": "施設名を入力してください",},
                                   )
    postal_code = forms.CharField(label ="郵便番号", max_length=8,
                                  widget=forms.TextInput(attrs={"placeholder": "例：123-4567"}),
                                  error_messages={"required": "郵便番号を入力してください",},
                                  )
    address = forms.CharField(label = "住所", max_length=100,
                                   error_messages={"required": "住所を入力してください",},
                              )
    phone_number = forms.CharField(label = "電話番号", max_length=15,
                                   widget=forms.TextInput(attrs={"placeholder": "例：090-1234-5678"}),
                                   error_messages={"required": "電話番号を入力してください",},
                                   )
    email = forms.EmailField(label = "メールアドレス",
                                   error_messages={"required": "メールアドレスを入力してください",
                                                   "invalid": "正しいメールアドレスを入力してください",},
                             )
    password1 = forms.CharField(label = "パスワード ※英数字８文字以上",widget=forms.PasswordInput,
                                   error_messages={"required": "パスワードを入力してください",},
                                )
    password2 = forms.CharField(label = "パスワード（確認用）",widget=forms.PasswordInput,
                                   error_messages={"required": "確認用パスワードを入力してください",},
                                )
        
    def clean(self):
        cleaned = super().clean()
        password1 = cleaned.get("password1")
        password2 = cleaned.get("password2")
        
        if password1:
            validate_alnum_password(password1)

        if password1 != password2:
            raise ValidationError("パスワードが一致しません")
        
        email = cleaned.get("email")

        if email and User.objects.filter(email=email).exists():
            raise ValidationError("このメールアドレスは既に使われています")
        
        return cleaned

# 保護者側の新規登録フォーム
class GuardianSignUpForm(forms.Form):
    invite_code = forms.CharField(label="認証コード", max_length=6,
                                   error_messages={"required": "認証コードを入力してください",},
                                  )
    child_name = forms.CharField(label="園児氏名", max_length=50,
                                   error_messages={"required": "園児氏名を入力してください",},
                                 )
    guardian_name = forms.CharField(label="保護者氏名", max_length=30,
                                   error_messages={"required": "保護者氏名を入力してください",},
                                 )       
    relationship = forms.ChoiceField(choices=[("","選択してください")] + list(Family.Relationship.choices), label="続柄",
                                   error_messages={"required": "続柄を選択してください",},
                                     )
    email = forms.EmailField(label="メールアドレス",
                                error_messages={"required": "メールアドレスを入力してください",
                                                "invalid": "正しいメールアドレスを入力してください",},
                             )
    password1 = forms.CharField(label="パスワード ※英数字８文字以上", widget=forms.PasswordInput,
                                   error_messages={"required": "パスワードを入力してください",},
                                )
    password2 = forms.CharField(label="パスワード（確認用）", widget=forms.PasswordInput,
                                error_messages={"required": "確認用パスワードを入力してください",},
                                )
    
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
    
    def clean(self):
        cleaned = super().clean()
        
        password1 = cleaned.get("password1")
        password2 = cleaned.get("password2")
        
        if password1:
            try:
                validate_alnum_password(password1)
            except ValidationError as e:
                self.add_error("password1", e)

        if password1 != password2:
            self.add_error("password2", "パスワードが一致しません")
  
    #園児名確認
        invite =cleaned.get("invite")
        child_name = cleaned.get("child_name")
    
        if invite and child_name and invite.child.name != child_name:
            self.add_error("child_name", "園児氏名が認証コードと一致しません")

        if not self.errors:
            email = cleaned.get("email")
            if email and User.objects.filter(email=email).exists():
                self.add_error("email", "このメールアドレスは既に使われています")

        return cleaned
    
    def save(self):
        invite = self.cleaned_data["invite"]
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

        family, created = Family.objects.get_or_create(
            guardian=user,
            child=child,
            defaults={"relationship": relationship},   
        )

        if not created and relationship is not None:
            family.relationship = relationship
            family.save(update_fields=["relationship"])

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
            (0,"パパ"),
            (1,"ママ"),
            (2,"おじいちゃん"),
            (3,"おばあちゃん"),
            (4,"その他"),
        ]

        # 続柄は変更できないようにする
        self.fields["relationship"].disabled = True

        last_name = self.instance.last_name or ""
        first_name = self.instance.first_name or ""
        full = f"{last_name} {first_name}".strip()
        self.fields["guardian_name"].initial = full
        self.fields["postal_code"].widget.attrs["placeholder"] = "例：123-4567"
        self.fields["phone_number"].widget.attrs["placeholder"] = "例：090-1234-5678"

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
    
        email = self.cleaned_data.get("email")
        
        if email :
            user.email = email
            user.username = email

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

        if new_password1:
            try:
                validate_alnum_password(new_password1)
            except ValidationError as e:
                self.add_error("new_password1", e)
        # 現在と同じパスワードを禁止
        if old_password and new_password1 and old_password == new_password1:
            self.add_error("new_password1", "現在と同じパスワードは設定できません")

        return cleaned_data

# パスワード再発行フォーム
class CustomPasswordResetForm(PasswordResetForm):

    email = forms.EmailField(
        label="メールアドレス",
        error_messages={
            "required": "メールアドレスを入力してください",
            "invalid": "正しいメールアドレスを入力してください",
        }
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")

        # 登録済みメールアドレスか確認
        if not User.objects.filter(email=email).exists():
            raise ValidationError(
                "そのメールアドレスは登録されていません。新規登録をしてください。"
            )

        return email

class CustomSetPasswordForm(SetPasswordForm):

    def clean_new_password1(self):
        password = self.cleaned_data.get("new_password1")

        if password and self.user.check_password(password):
            raise ValidationError(
                "現在と同じパスワードは設定できません"
            )

        return password