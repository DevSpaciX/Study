# Generated by Django 4.2 on 2023-06-16 06:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0007_employee'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='email',
            field=models.EmailField(max_length=254, null=True),
        ),
    ]
