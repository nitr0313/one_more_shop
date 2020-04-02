# Generated by Django 3.0.4 on 2020-04-01 07:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='description',
            field=models.CharField(blank=True, default='', max_length=1000, verbose_name='Описание'),
        ),
        migrations.AddField(
            model_name='item',
            name='discount',
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateField(auto_now_add=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.Item')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Предмет помещенный в избранное',
                'verbose_name_plural': 'Избранное',
                'ordering': ('item', 'create_date'),
            },
        ),
        migrations.CreateModel(
            name='ItemRating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.CharField(choices=[('5', 5), ('4', 4), ('3', 3), ('2', 2), ('1', 1)], default='5', max_length=1, verbose_name='Мнение пользователя о книге')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item_rating', to='shop.Item')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Отценка пользователя',
                'verbose_name_plural': 'Отценки пользователей',
                'ordering': ('item', 'rating'),
                'unique_together': {('item', 'user')},
            },
        ),
    ]
