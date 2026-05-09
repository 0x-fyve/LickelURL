from django.contrib import admin
from . models import ShortURL, CustomUser
from django.contrib.auth.admin import UserAdmin
# Register your models here.
admin.site.register(ShortURL)
admin.site.register(CustomUser, UserAdmin)