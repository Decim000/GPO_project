from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    company_name = models.CharField(max_length=250, blank=True)
    phone_number = models.CharField(max_length=12, blank=True)
    email = models.CharField(max_length=50, blank=True)

