from django.db import models
from nurseries.models import Nursery, Classroom

class Child(models.Model):
    
    nursery = models.ForeignKey(
        Nursery,
        on_delete=models.CASCADE,
        related_name="children",
        verbose_name="園",
        )
    
    classroom = models.ForeignKey(
        Classroom, 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True, 
        related_name="children",
        verbose_name="クラス",
        )  
    
    name = models.CharField(
        "氏名",
        max_length=50,
    )
    
    withdrawn_month = models.DateField(
        "退園月",
        null=True,
        blank=True,
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
        verbose_name = "園児"
        verbose_name_plural = "園児一覧"
        ordering = ["nursery", "classroom", "name"]
    
    def __str__(self):
        return f"{self.name}"
    