from django import forms
from .models import Nursery


class NurseryMyPageForm(forms.ModelForm):

    email = forms.EmailField(
        label="メールアドレス",
        widget=forms.EmailInput(attrs={"class": "mypage-input"})
    )

    class Meta:
        model = Nursery
        fields = ["name", "postal_code", "address", "phone_number"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "mypage-input"}),
            "postal_code": forms.TextInput(attrs={"class": "mypage-input"}),
            "address": forms.TextInput(attrs={"class": "mypage-input"}),
            "phone_number": forms.TextInput(attrs={"class": "mypage-input"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)

        super().__init__(*args, **kwargs)

        self.user = user

        if user:
            self.fields["email"].initial = user.email

    def clean_email(self):
        email = self.cleaned_data["email"]

        exists = (
            self.user.__class__.objects
            .filter(email=email)
            .exclude(pk=self.user.pk)
            .exists()
        )

        if exists:
            raise forms.ValidationError(
                "このメールアドレスは既に使用されています"
            )

        return email

    def save(self, commit=True):
        nursery = super().save(commit=False)

        if self.user:
            self.user.email = self.cleaned_data["email"]

            # username=email運用ならこれも必要
            self.user.username = self.cleaned_data["email"]

            self.user.save()

        if commit:
            nursery.save()

        return nursery