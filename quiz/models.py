import os

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User

# Create your models here.
from bizicoTest import settings


def get_image_path(instance, filename):
    return os.path.join('image', filename)


class User(AbstractUser):
    rate = models.FloatField(default=0.0, blank=True)
    image = models.ImageField(upload_to=get_image_path, blank=True, null=True)

    def __str__(self):
        return self.username

    """
    Checks if user is already in database
    """
    def check_existence(self):
        error = None
        try:
            User.objects.get(email=self.email)
            error = "Email already exist."
        except ObjectDoesNotExist:
            pass
        try:
            User.objects.get(username=self.username)
            error = "Username already exist."
        except ObjectDoesNotExist:
            pass
        return error


class Quiz(models.Model):
    name = models.CharField(max_length=256, blank=False)
    description = models.TextField(max_length=512, blank=True)

    points = models.IntegerField(blank=True)

    author = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False)

    date = models.DateTimeField(blank=True)

    def __str__(self):
        return self.name


class Question(models.Model):
    to = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    value = models.TextField(max_length=512)
    image = models.ImageField(upload_to=get_image_path, blank=True, null=True)
    points = models.IntegerField(blank=True, default=1)

    def __str__(self):
        return self.value


class Answer(models.Model):
    to = models.ForeignKey(Question, on_delete=models.CASCADE)
    value = models.TextField(max_length=256)
    correct = models.BooleanField(default=False)

    def __str__(self):
        return self.value


class Record(models.Model):
    by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False, on_delete=models.CASCADE)
    to = models.ForeignKey(Quiz, blank=False, on_delete=models.CASCADE)

    date = models.DateTimeField(blank=False)
    points = models.IntegerField(blank=True)

    def __str__(self):
        return self.by + "->" + self.to + " = " + self.points
