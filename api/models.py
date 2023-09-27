from django.contrib.auth.models import User
from django.db import models
from .utils import upload_image_path


class Message(models.Model):
    role = models.CharField(max_length=255)
    content = models.TextField()
    time = models.BigIntegerField()
    status = models.BooleanField(default=False)


class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    messages = models.ManyToManyField(Message)


class ChatImages(models.Model):
    image = models.ImageField(upload_to=upload_image_path)