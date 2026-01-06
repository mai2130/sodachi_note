from django.db import models
from django.contrib.auth.models import AbstractUser
from children.models import Child

class User(AbstractUser): 
    
    active_child = models.ForeignKey(
        Child,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="active_users",
        verbose_name="現在選択中の園児"
        )
    
    class Role(models.IntegerChoices):
        FACILITY = 0, '園'
        GUARDIAN = 1, '保護者'
        
    role = models.PositiveSmallIntegerField(
        choices=Role.choices,
        default=Role.GUARDIAN
    )
    email = models.EmailField(unique=True)
   
    def is_facility(self):
        return self.role == self.Role.FACILITY

    def is_guardian(self):
        return self.role == self.Role.GUARDIAN