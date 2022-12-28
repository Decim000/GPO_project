import json
from django.utils.timezone import now
from email.policy import default
from django.db import models
from accounts.models import CustomUser


class KeyWords(models.Model):
    keywords = models.JSONField(blank=True, null=True)
    searcher = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return " ".join([str(self.pk)])


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


class SupplierDefinition(models.Model):
    supplier_definition_name = models.CharField(max_length=250, unique=True)

    def __str__(self):
        return self.supplier_definition_name


class Tender(models.Model):
    number = models.CharField(max_length=250, default='---')
    name = models.CharField(max_length=250, default='---')
    tenderType = models.CharField(max_length=250, default='---')
    price = models.FloatField(default=0)
    supplier_definition = models.ForeignKey(
        SupplierDefinition, on_delete=models.SET_NULL, null=True)
    platform_URL = models.CharField(max_length=250, default='---')
    platform = models.CharField(
        max_length=250, default='---', blank=True, null=True)
    purchase_stage = models.ForeignKey(
        PurchaseStage, on_delete=models.SET_NULL, null=True)
    placement_date = models.DateTimeField(default=now, blank=True)
    start_date = models.DateTimeField(default=now, blank=True)
    end_date = models.DateTimeField(default=now, blank=True)
    federal_law = models.ForeignKey(
        FederalLaw, on_delete=models.SET_NULL, null=True)
    deadline = models.DateTimeField(default=now, blank=True)
    stack_technologies = models.ForeignKey(
        Technology, on_delete=models.SET_NULL, null=True)
    percentage_application_security = models.FloatField(default=10)
    access_restrictions = models.BooleanField(default=False)
    technical_specification = models.CharField(max_length=1000, default='---')

    def __str__(self):
        return self.name


def directory_path(instance, filename):

    # file will be uploaded to MEDIA_ROOT / <number>/<filename>
    return 'media/docs/{0}/{1}'.format(str(instance.tender.number), filename)


class TenderDocument(models.Model):
    tender = models.ForeignKey(Tender, on_delete=models.SET_NULL, null=True)
    document = models.FileField(upload_to=directory_path, null=True)
    title = models.CharField(max_length=250, default="---")

    def __str__(self):
        return self.title


class Report(models.Model):
    name = models.CharField(max_length=250)
    time_created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    file = models.FileField(upload_to='reports/')
    tenders = models.ManyToManyField(Tender)

    def __str__(self):
        return self.name
