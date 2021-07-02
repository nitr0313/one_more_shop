from django.db import models

# Create your models here.

ORDER_STATUSES = (
    ('0','Заказан'),
    ('1','Оплачен'),
    ('2','В доставке'),
    ('3','Доставлен'),
    ('4','Выполнен'),
    ('5','Анулирован'),
    )

class Order(models.Model):
    customer = models.ForeignKey('account.Profile', verbose_name="Заказчик", on_delete=models.CASCADE,
                                    related_name="order")
    created = models.DateTimeField(verbose_name="Созадана", auto_now_add=True)
    updated = models.DateTimeField(verbose_name="Обновлен", auto_now=True)
    ordered = models.BooleanField(default=False)
    status = models.CharField(max_length=1, choices=ORDER_STATUSES, default='1')

    class Meta:
        ordering = ['-created']
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f'Заказ: {self.id} от {self.created}'

    @property
    def sum_order_price(self):
        # price_items = OrderItems.objects.filter(order=self).aggregate(Sum('full_price'))
        items = OrderItems.objects.filter(order=self)
        price = sum([ item.full_price for item in items ])
        return price

    def get_status(self):
        return ORDER_STATUSES[int(self.status)][1]


class OrderItems(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='cart_item')
    item = models.ForeignKey('shop.Item', on_delete=models.CASCADE)
    price_on_order_date = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.order.customer} {self.item} {self.price_on_order_date}"

    @property
    def full_price(self):
        return self.price_on_order_date * self.quantity

    class Meta:
        verbose_name = 'Заказанный товар'
        verbose_name_plural = 'Заказанные товары'
