from django.db import models
import json
from django.contrib.auth.models import User

# Create your models here.

class Memory(models.Model):
    date = models.DateField()
    emotion = models.CharField(max_length=64)
    description = models.CharField(max_length=64)
    content = models.TextField(null=True )
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True )

    def __str__(self):
        return f'{self.user.username} : {self.description} : {self.emotion}'

class Biographyitem(models.Model):
    item = models.CharField(max_length=64)
    description = models.CharField(max_length=64)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
    username = self.user.username if self.user else 'No Field'
    item = self.user.item if self.user else 'No Field'
    description = self.user.description if self.user else 'No Field'
    return f'{username}: {self.item} : {self.description}'


class Chat(models.Model):
    messages = models.JSONField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
   
    def __str__(self):
        return f'{self.user.username} : {self.messages}'
    
class Domain(models.Model):
    domain = models.CharField(max_length=64)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.user.username} : {self.domain}'