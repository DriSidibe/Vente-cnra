from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    api_key = models.CharField(max_length=255, blank=True, null=True)
    api_key_expiration_datetime = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.username