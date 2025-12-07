from django.db import models
from nurseries.models import Nursery,Classroom


class Notice(models.Model):
    class Category(models.IntegerChoices):
        DAILY = 0, "日常生活"
        EVENT = 1, "行事"
        REQUEST = 2, "お願い"
        IMPORTANT = 3, "重要"
        OTHER = 4, "その他"
        
    nursery = models.ForeignKey(
        Nursery,
        on_delete=models.CASCADE,
        related_name='notices',
        verbose_name='園'
    )
    
    date = models.DateField('日付')
    category = models.PositiveSmallIntegerField(
        'カテゴリ',
        choices=Category.choices,
        default=Category.DAILY,
    )
    
    title = models.CharField('タイトル',max_length=50)
    body = models.TextField('本文')
    file = models.FileField(
        '添付資料',
        upload_to="notices/",
        blank=True,
        null=True,
    )
    
    classrooms = models.ManyToManyField(
        Classroom,
        through='NoticeClassroom',
        related_name='notices',
        blank=True,
        verbose_name='対象クラス',
    )
    
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    def __str__(self):
        return self.title
    
class NoticeClassroom(models.Model):
    notice = models.ForeignKey(
        Notice,
        on_delete=models.CASCADE,
        verbose_name='おたより',
    )
    
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        verbose_name='クラス',
    )
    
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)
    
    class Meta:
        unique_together = ('notice', 'classroom')
        verbose_name = 'おたより対象クラス'
        verbose_name_plural = 'おたより対象クラス'
        
    def __str__(self):
        return f"{self.notice.title} - {self.classroom.name}"