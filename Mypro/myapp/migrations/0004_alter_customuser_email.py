# Generated by Django 5.0.3 on 2024-04-02 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0003_remove_customuser_user_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="email",
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]