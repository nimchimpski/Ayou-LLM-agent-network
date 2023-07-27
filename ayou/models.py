from django.db import models
import json

# Create your models here.

class Memory(models.Model):
    date = models.DateField()
    emotion = models.CharField(max_length=64)
    description = models.CharField(max_length=64)
    content = models.TextField(null=True )
    id = models.AutoField(primary_key=True)

    def __str__(self):
        return f'{self.date} : {self.description} : {self.emotion}'

class Biographyitem(models.Model):
    item = models.CharField(max_length=64)
    description = models.CharField(max_length=64)


    def __str__(self):
        return f'{self.id} : {self.item} : {self.description}'

class Chat(models.Model):
    messages = models.JSONField(null=True)
   
    def __str__(self):
        return f'{self.id} : {self.messages}'