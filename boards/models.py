from django.db import models
from django.conf import settings
from nurseries.models import Nursery

class Board(models.Model):
    class Category(models.IntegerChoices):
        DAILY = 0, '日常生活'
        EVENT = 1, '行事'
        OTHER = 2, 'その他' 
       
    nursery = models.ForeignKey(Nursery, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    date = models.DateField()
    category = models.PositiveSmallIntegerField(choices=Category.choices)
    title = models.CharField(max_length=100)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
class BoardPost(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='posts')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    comment = models.CharField(max_length=255)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

