from django.db import models
from django.conf import settings


class Nursery(models.Model):
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

    def __str__(self) :
        return self.name
    
class Classroom(models.Model):
    nursery = models.ForeignKey(
        Nursery,
        on_delete=models.CASCADE,
        related_name="classrooms",
        verbose_name="園",
        )
    name = models.CharField(
        "クラス名",
        max_length=30,
    )
    created_at = models.DateTimeField(
        "作成日時",
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        "更新日時",
        auto_now=True,
    )
        
    class Meta:
        verbose_name = "クラス"
        verbose_name_plural = "クラス一覧"
        ordering = ["nursery", "name"]
        unique_together = ("nursery", "name")
            
    def __str__(self):
        return f"{self.nursery.name}/{self.name}"