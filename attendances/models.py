from django.db import models
from children.models import Child

class Attendance(models.Model):
    class Status(models.IntegerChoices):
        PRESENT = 0, '出席'
        LATE_EARLY = 1, '遅刻・早退'
        ABSENT = 2 ,'欠席'
        
    child = models.ForeignKey(
        Child, 
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name='園児' 
    )
    date = models.DateField(verbose_name='日付')
    status = models.PositiveSmallIntegerField(
        "出欠",
        choices=Status.choices,
    ) 
    
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)
    
    class Meta:
        # 制約
        constraints = [
            models.UniqueConstraint(
                fields=['child', 'date'],
                name='unique_child_date'
            )
        ]
        # インデックス（検索高速化）
        indexes = [
            models.Index(fields=['child', 'date']),
            models.Index(fields=['date']),
        ]
        
    def __str__(self):
        return f"{self.child} - {self.date} - {self.get_status_display()}"