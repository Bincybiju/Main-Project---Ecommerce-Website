# Generated by Django 5.0.3 on 2024-04-08 05:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="orderstatus",
            options={},
        ),
        migrations.RemoveField(
            model_name="orderstatus",
            name="updated_at",
        ),
        migrations.AlterField(
            model_name="orderstatus",
            name="status",
            field=models.CharField(
                choices=[
                    ("Pending", "Pending"),
                    ("Shipped", "Shipped"),
                    ("Delivered", "Delivered"),
                    ("Cancelled", "Cancelled"),
                ],
                default="Pending",
                max_length=20,
            ),
        ),
    ]