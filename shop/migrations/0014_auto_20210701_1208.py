# Generated by Django 3.0.5 on 2021-07-01 09:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0013_auto_20200429_0931'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderItems',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price_on_order_date', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity', models.IntegerField(default=1)),
            ],
            options={
                'verbose_name': 'Товар из заказа',
                'verbose_name_plural': 'Товары в заказах',
            },
        ),
        migrations.RemoveField(
            model_name='cartitems',
            name='item',
        ),
        migrations.RemoveField(
            model_name='cartitems',
            name='order',
        ),
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('1', 'Заказан'), ('2', 'Выполнен')], default='1', max_length=1),
        ),
        migrations.AlterField(
            model_name='item',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена'),
        ),
        migrations.AlterField(
            model_name='item',
            name='quantity_unit',
            field=models.CharField(choices=[('шт', 'шт'), ('г', 'грамм'), ('кг', 'килограмм'), ('м', 'метр'), ('см', 'сантиметр'), ('мм', 'милиметр')], default='шт', max_length=2),
        ),
        migrations.AlterField(
            model_name='itemrating',
            name='rating',
            field=models.CharField(choices=[('5', 5), ('4', 4), ('3', 3), ('2', 2), ('1', 1)], default='5', max_length=1, verbose_name='Мнение пользователя о товаре'),
        ),
        migrations.DeleteModel(
            name='Cart',
        ),
        migrations.DeleteModel(
            name='CartItems',
        ),
        migrations.AddField(
            model_name='orderitems',
            name='item',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='shop.Item'),
        ),
        migrations.AddField(
            model_name='orderitems',
            name='order',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cart_item', to='shop.Order'),
        ),
    ]