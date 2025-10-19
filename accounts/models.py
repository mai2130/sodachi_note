from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Role(models.IntegerChoices):
        NURSERY = 0, '園'
        GUARDIAN = 1, '保護者'
    role = models.PositiveSmallIntegerField(choices=Role.choices, default=Role.GUARDIAN)
    email = models.EmailField(unique=True)
    
    def is_nursery(self) -> bool:
        return self.role == self.Role.GUARDIAN
    
    def is_guardian(self) -> bool:
        return self.role == self.Role.GUARDIAN
    
    def __str__(self) -> str:
        return f'{self.username}({self.get_role_display()})'