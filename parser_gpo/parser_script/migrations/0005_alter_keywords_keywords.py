# Generated by Django 4.1.1 on 2022-11-23 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("parser_script", "0004_alter_keywords_keywords"),
    ]

    operations = [
        migrations.AlterField(
            model_name="keywords",
            name="keywords",
            field=models.JSONField(blank=True, null=True),
        ),
    ]