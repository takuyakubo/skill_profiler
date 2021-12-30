from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.


class UProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    current_point = models.IntegerField(default=0)


class PraiseHistory(models.Model):
    from_who = models.ForeignKey(User, related_name="sent_histories", on_delete=models.DO_NOTHING)
    to_who = models.ForeignKey(User, related_name="recv_histories", on_delete=models.DO_NOTHING)
    reasons = models.TextField(blank=True, default='')
    sent_at = models.DateTimeField(auto_now_add=True)
