from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    #recenseado = models.BooleanField(default=False)
    # username = models.CharField(max_length=20, unique=True, null=True, blank=True)
    # first_name = models.CharField(max_length=50, null=True, blank=True)
    # last_name = models.CharField(max_length=100, null=True, blank=True)
    nim = models.CharField(max_length=20, unique=True, null=True, blank=True)

    def __str__(self):
        return self.username
