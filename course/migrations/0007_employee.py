# Generated by Django 4.2 on 2023-06-15 18:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0006_alter_test_lecture'),
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('work_time', models.CharField(max_length=100)),
                ('line', models.CharField(max_length=100)),
            ],
        ),
    ]
