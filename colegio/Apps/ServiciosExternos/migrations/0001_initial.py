# Generated by Django 2.1 on 2025-03-22 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AccesosExternos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255, unique=True)),
                ('url', models.URLField(max_length=500)),
                ('token', models.CharField(max_length=500)),
            ],
        ),
    ]
