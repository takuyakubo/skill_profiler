from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.


class UProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    current_point = models.IntegerField(default=0)
