# Generated by Django 5.1.2 on 2024-11-13 03:50

import bankoffers.models
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="BankOffer",
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
                    "boid",
                    models.CharField(
                        default=bankoffers.models.gen_uuid4_boid,
                        max_length=64,
                        unique=True,
                    ),
                ),
                ("bank_name", models.CharField(max_length=255)),
                ("bank_image", models.URLField(max_length=255)),
                ("offer_details", models.TextField()),
                ("offer_url", models.URLField(max_length=255)),
                ("offer_details_url", models.URLField(max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
