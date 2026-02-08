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
        default=Role.GUARDIAN,
        verbose_name="権限",
    )

    class Relationship(models.IntegerChoices):
        FATHER = 0, "父"
        MOTHER = 1, "母"
        GRANDFATHER = 2, "祖父"
        GRANDMOTHER = 3, "祖母"
        OTHER = 4, "その他"

    relationship = models.PositiveSmallIntegerField(
        "続柄",
        choices=Relationship.choices,
        null = True,
        blank=True,
    )

    email = models.EmailField(unique=True)
    postal_code = models.CharField("郵便番号", max_length=8, blank=True, default="")
    address = models.CharField("住所", max_length=100,blank=True,default="")
    phone_number = models.CharField("電話番号", max_length=15,blank=True,default="")

    def is_facility(self):
        return self.role == self.Role.FACILITY

    def is_guardian(self):
        return self.role == self.Role.GUARDIAN