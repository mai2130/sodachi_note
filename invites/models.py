from django.db import models
from children.models import Child
import uuid

class InviteCode(models.Model):
    child = models.ForeignKey(
        Child,
        on_delete=models.CASCADE,
        related_name='invite_codes'
    )

    # UUIDをそのまま保存（一意＆自動生成）
    code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    # 何人がこのコードを使ったか（0以上）
    users_count = models.PositiveIntegerField(default=0)

    # “最大何人まで使えるか” の上限（例：兄弟や保護者複数想定など）
    max_uses = models.PositiveIntegerField(default=5)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_available(self) -> bool:
        return self.users_count < self.max_uses

    def __str__(self) -> str:
        return f"{self.child} - {self.code}"

