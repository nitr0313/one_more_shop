# Generated by Django 3.0.4 on 2020-04-02 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_auto_20200402_1209'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='slug',
            field=models.SlugField(default=0, verbose_name='ЧПУ'),
        ),
    ]