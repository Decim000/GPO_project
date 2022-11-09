from django.utils.timezone import now
from email.policy import default
from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    company_name = models.CharField(max_length=250, blank=True)
    phone_number = models.CharField(max_length=12, blank=True)
    email = models.CharField(max_length=50, blank=True)


class KeyWords(models.Model):
    keywords = models.CharField(max_length = 250, blank=True)
    searcher = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return " ".join([self.keywords, self.searcher])


class FederalLaw(models.Model):
    name = models.CharField(max_length=250)
    number = models.IntegerField()

    def __str__(self):
        return self.name


class Technology(models.Model):
    name = models.CharField(max_length=250, unique=True)

    def __str__(self):
        return self.name


class PurchaseStage(models.Model):
    name = models.CharField(max_length=250, unique=True)

    def __str__(self):
        return self.name


class Tender(models.Model):
    number = models.IntegerField()
    name = models.CharField(max_length=250, default='---')
    tenderType = models.CharField(max_length=250, default='---')
    price = models.FloatField(default=0)
    platform = models.CharField(max_length=250, default='---', blank=True, null=True)
    purchase_stage = models.ForeignKey(PurchaseStage, on_delete=models.SET_NULL, null=True)
    placement_date = models.DateTimeField(default=now, blank=True)
    start_date = models.DateTimeField(default=now, blank=True)
    end_date = models.DateTimeField(default=now, blank=True)
    federal_law = models.ForeignKey(FederalLaw, on_delete=models.SET_NULL, null=True)
    deadline = models.DateTimeField(default=now, blank=True)
    stack_technologies = models.ForeignKey(Technology, on_delete=models.SET_NULL, null=True)
    percentage_application_security = models.FloatField(default=10)
    access_restrictions = models.BooleanField(default=False)
    technical_specification = models.CharField(max_length=1000, default='---')

    def __str__(self):
        return self.name


class Report(models.Model):
    name = models.CharField(max_length=250)
    time_created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    file = models.FileField(upload_to='reports/')
    tenders = models.ManyToManyField(Tender)

    def __str__(self):
        return self.name

