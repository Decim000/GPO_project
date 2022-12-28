from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    company_name = models.CharField(max_length=250, blank=True)
    phone_number = models.CharField(max_length=12, blank=True)
    email = models.CharField(max_length=255, unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def get_full_name(self):
        return self.first_name

    def get_short_name(self):
        return self.first_name

    def __str__(self):
        return str(self.id)


class Profile(models.Model):
    user = models.OneToOneField(
        CustomUser, null=True, on_delete=models.CASCADE)
