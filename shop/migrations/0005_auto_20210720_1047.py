# Generated by Django 3.0.5 on 2021-07-20 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_auto_20210720_1011'),
    ]

    operations = [
        migrations.AlterField(
            model_name='specvalue',
            name='value',
            field=models.CharField(max_length=150, verbose_name='Значение характеристики'),
        ),
    ]
