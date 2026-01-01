from django.db import models
from children.models import Child
import uuid
import secrets #セキュリティ的に安全なランダム値を作る（招待コード向き）
import string #英数字の文字セット（A-Z や 0-9）を簡単に用意する

# 6文字コードを作る関数
def generate_short_code(length: int = 6) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

class InviteCode(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='invite_codes')

    # UUID（一意＆自動生成）内部用
    code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    # 短縮コード（6文字）外部表示用
    short_code = models.CharField(max_length=6, unique=True, db_index=True, editable=False)

    # 利用人数（0以上）
    users_count = models.PositiveIntegerField(default=0)

    # 利用上限（5人）
    max_uses = models.PositiveIntegerField(default=5)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_available(self):
        return self.users_count < self.max_uses
    
    def save(self, *args, **kwargs):
        if not self.short_code:
            for _ in range(50):  # 最大50回試行
                candidate = generate_short_code(6)
                if not InviteCode.objects.filter(short_code=candidate).exists():
                    self.short_code = candidate
                    break
            else:
                raise RuntimeError("短縮コードの生成に失敗しました。")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.child} - {self.short_code}"

