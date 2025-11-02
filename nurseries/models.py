from django.db import models
from django.conf import settings


class Nursery(models.Model):
    # 施設アカウントのUserと1対1
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="nursery",
    )

    name = models.CharField("施設名", max_length=100)
    postal_code = models.CharField("郵便番号", max_length=8)
    address = models.CharField("住所", max_length=100)
    phone_number = models.CharField("電話番号", max_length=15)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name