# Generated by Django 2.1 on 2025-03-22 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Pagos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Dni', models.CharField(default='-', max_length=10)),
                ('PagoMes', models.CharField(default='-', max_length=20)),
                ('PagoAno', models.CharField(default='-', max_length=4)),
            ],
        ),
    ]
