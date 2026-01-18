from django.db import models
from datetime import date
from children.models import Child

class GrowthLog(models.Model):
    
    class Source(models.TextChoices):
        HOME = "home" , "家庭"
        SCHOOL = "school" , "園"
        
    class Appetite(models.IntegerChoices):
        YES = 0, "あり"
        NO = 1, "なし"
        
        
    CONDITION_CHOICES = [
        (0,"異常なし"),
        (1,"発熱"),
        (2,"鼻水"),
        (3,"咳"),
        (4,"下痢"),
        (5,"嘔吐"),
    ]
    POO_CHOICES = [(0,"あり"), (1,"なし")]
    LUNCH_CHOICES = [(0,"完食"), (1,"残す")]
    
   
    child = models.ForeignKey(
        Child, 
        on_delete=models.CASCADE, 
        related_name='growthlogs',
        verbose_name="園児",
        )
    
    source = models.CharField(
        "記録元",
        max_length=10,
        choices = Source.choices,
        default = Source.SCHOOL,
    )
    
    date = models.DateField("日付",default=date.today)
    
    # 家庭側
    home_bedtime = models.TimeField("就寝時間", null=True, blank=True)
    home_wake_up_time = models.TimeField("起床時間", null=True, blank=True)
    home_appetite = models.PositiveSmallIntegerField("食欲", choices=Appetite.choices, null=False, blank=False,default=0,)  
    home_condition = models.PositiveSmallIntegerField("家庭の体調", choices=CONDITION_CHOICES, null=True, blank=True, default=0)
    home_temperature = models.DecimalField("体温", max_digits=3, decimal_places=1, null=True, blank=True, default=36.5)
    home_poo = models.IntegerField("排便", choices=POO_CHOICES, null=False, blank=False, default=0 )
    home_state = models.TextField("様子", max_length=255, blank=True)

    # 園側
    school_lunch= models.IntegerField(
        "昼食",
        choices=LUNCH_CHOICES, 
        null=False,
        blank=False,
        default=0
        ) 
    
    school_nap_start = models.TimeField(
        "午睡時間",
        null=True,
        blank=True
        )
    school_nap_end = models.TimeField(
        null=True,
        blank=True
        )
 
    school_poo = models.IntegerField(
        "排便",
        choices=POO_CHOICES,
        null=False,
        blank=False,
        default=0
        )
    
    school_condition = models.PositiveSmallIntegerField("家庭の体調", choices=CONDITION_CHOICES, null=True, blank=True, default=0)

    school_temperature = models.DecimalField(
        "体温",
        max_digits=3,
        decimal_places=1,
        null=True, 
        blank=True,
        default=36.5
        )

    school_state = models.TextField(
        "様子",
        max_length=255,
        blank=True
        )
    
    # 共通項目
    submitted = models.BooleanField("提出済み", default=False)
    created_at = models.DateTimeField("作成日時",auto_now_add=True) 
    updated_at = models.DateTimeField("更新日時",auto_now=True)

    class Meta:
        verbose_name = ("生活・成長記録")
        verbose_name_plural = ("生活・成長記録")
        constraints = [models.UniqueConstraint(fields=["child", "source", "date"], name="unique_child_source_date")]
        
        ordering = ["-date","child"]

    def __str__(self):
        return f"{self.child.name} {self.date} ({self.source})"