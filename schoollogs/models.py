from django.db import models
from datetime import date
from children.models import Child

class SchoolGrowthLog(models.Model):
    CONDITION_CHOICES = [
        (0,"異常なし"),
        (1,"発熱"),
        (2,"鼻水"),
        (3,"咳"),
        (4,"下痢"),
        (5,"嘔吐"),
    ]
    POO_CHOICES = [
        (0,"あり"),
        (1,"なし"),
    ]
    
    LUNCH_CHOICES = [
        (0,"完食"),
        (1,"残す"),
    ]
    
    child = models.ForeignKey(
        "children.Child", 
        on_delete=models.CASCADE, 
        related_name='school_growth_logs',
        verbose_name="園児",
        )
    
    date = models.DateField("日付",default=date.today)
    condition = models.IntegerField(
        "体調",
        choices=CONDITION_CHOICES,
        default=0,
        )
    temperature = models.DecimalField(
        "体温",
        max_digits=3,
        decimal_places=1,
        null=True, 
        blank=True,
        default=36.5
        )
    poo = models.IntegerField(
        "排便",
        choices=POO_CHOICES,
        null=False,
        blank=False,
        default=0,
        )   
    nap_start = models.TimeField(
        "午睡時間",
        null=True,
        blank=True,
        )
    nap_end = models.TimeField(
        null=True,
        blank=True,
        )

    lunch = models.IntegerField(
        "昼食",
        choices=LUNCH_CHOICES, 
        null=False,
        blank=False,
        default=0,
        ) 
    state = models.TextField(
        "様子",
        max_length=255,
        blank=True,
        )
    created_at = models.DateTimeField("作成日時",auto_now_add=True) 
    updated_at = models.DateTimeField("更新日時",auto_now=True)

    class Meta:
        verbose_name = ("園での生活・成長記録")
        verbose_name_plural = ("園での生活・成長記録")
        unique_together = ('child', 'date')
        ordering = ["-date","child"]

    def __str__(self):
        return f"{self.child.name} {self.date}"