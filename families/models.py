# families/models.py
from django.db import models
from django.conf import settings #AUTH_USER_MODEL（カスタムUser）を参照
from children.models import Child

# 保護者（User）と園児（Child）を紐づける中間テーブル
class Family(models.Model):
    guardian = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="family_links",
        verbose_name="保護者"
    )

    child = models.ForeignKey(
        Child,
        on_delete=models.CASCADE,
        related_name="family_links",
        verbose_name="園児"
    )

    class Relationship(models.IntegerChoices):
        FATHER = 0, "父"
        MOTHER = 1, "母"
        GRANDFATHER = 2, "祖父"
        GRANDMOTHER = 3, "祖母"
        OTHER = 4, "その他"

    relationship = models.PositiveSmallIntegerField(
        "続柄",
        choices=Relationship.choices,
    )

    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        verbose_name = "家族リンク"
        verbose_name_plural = "家族リンク"
# 保護者×園児の組み合わせは1つだけ（重複登録防止）
        constraints = [
            models.UniqueConstraint(
                fields=["guardian", "child"],
                name="unique_guardian_child"
            )
        ]
# 検索を速くする（任意）
        indexes = [
            models.Index(fields=["child"]),
            models.Index(fields=["guardian"]),
        ]

    def __str__(self):
        return f"{self.child.name} - {self.guardian} ({self.get_relationship_display()})"

