from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

class ClickEvent(models.Model):

    short_url = models.ForeignKey(
        "ShortURL",
        on_delete=models.CASCADE,
        related_name="click_events"
    )
    
    device = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    browser = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True
    )

    clicked_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.browser} - {self.device}"

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
    