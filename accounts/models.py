from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser): 
    
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