from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]


class Profile(models.Model):
    name = models.CharField(max_length=50)
    

class ShortURL(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="urls"
    )

    original_url = models.URLField()
    short = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    clicks = models.IntegerField(default=0)

    def __str__(self):
        return self.short
    