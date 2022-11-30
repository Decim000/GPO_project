# Generated by Django 4.1.1 on 2022-11-13 13:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import parser_script.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="FederalLaw",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=250)),
                ("number", models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="PurchaseStage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=250, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="SupplierDefinition",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "supplier_definition_name",
                    models.CharField(max_length=250, unique=True),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Technology",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=250, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="Tender",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("number", models.CharField(default="---", max_length=250)),
                ("name", models.CharField(default="---", max_length=250)),
                ("tenderType", models.CharField(default="---", max_length=250)),
                ("price", models.FloatField(default=0)),
                ("platform_URL", models.CharField(default="---", max_length=250)),
                (
                    "platform",
                    models.CharField(
                        blank=True, default="---", max_length=250, null=True
                    ),
                ),
                (
                    "placement_date",
                    models.DateTimeField(blank=True, default=django.utils.timezone.now),
                ),
                (
                    "start_date",
                    models.DateTimeField(blank=True, default=django.utils.timezone.now),
                ),
                (
                    "end_date",
                    models.DateTimeField(blank=True, default=django.utils.timezone.now),
                ),
                (
                    "deadline",
                    models.DateTimeField(blank=True, default=django.utils.timezone.now),
                ),
                ("percentage_application_security", models.FloatField(default=10)),
                ("access_restrictions", models.BooleanField(default=False)),
                (
                    "technical_specification",
                    models.CharField(default="---", max_length=1000),
                ),
                (
                    "federal_law",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="parser_script.federallaw",
                    ),
                ),
                (
                    "purchase_stage",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="parser_script.purchasestage",
                    ),
                ),
                (
                    "stack_technologies",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="parser_script.technology",
                    ),
                ),
                (
                    "supplier_definition",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="parser_script.supplierdefinition",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TenderDocument",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "document",
                    models.FileField(
                        null=True, upload_to=parser_script.models.directory_path
                    ),
                ),
                ("title", models.CharField(default="---", max_length=250)),
                (
                    "tender",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="parser_script.tender",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Report",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=250)),
                ("time_created", models.DateTimeField(auto_now_add=True)),
                ("file", models.FileField(upload_to="reports/")),
                ("tenders", models.ManyToManyField(to="parser_script.tender")),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="KeyWords",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("keywords", models.CharField(blank=True, max_length=250)),
                (
                    "searcher",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
