from django.contrib.auth import get_user_model
from django.db import models
# from django.utils.text import slugify
from pytils.translit import slugify
from django.utils.safestring import mark_safe
from django.urls.base import reverse
import datetime
from django.db.models import Sum
from django.utils import timezone

User = get_user_model()

UNIT_CHOICE = (
    ('0', 'шт'),
    ('1', 'кг'),
    ('2', 'метр'),

)


class Item(models.Model):
    slug = models.SlugField(unique=True, verbose_name='URL', allow_unicode=True, blank=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=150, db_index=True, unique=True, verbose_name="Название")
    description = models.TextField(max_length=1000, db_index=True, verbose_name="Описание", blank=True, default="")
    price = models.FloatField(verbose_name="Цена", default=0.0)
    photo = models.ImageField(verbose_name="Фото", upload_to='items/%Y/%m/%d', blank=True)
    in_stock = models.BooleanField(verbose_name='В продаже', default=True)
    on_delete = models.BooleanField(verbose_name='Пометить на удаление', default=False)
    # rating = models.FloatField(verbose_name="Рейтинг", default=0.0)
    # discount = models.IntegerField(default=0)
    detail_url = 'item_detail_url'
    quantity_unit = models.CharField(max_length=2, choices=UNIT_CHOICE, default="0")

    def __str__(self):
        return f'{self.id} {self.title} {self.price}'

    @property
    def category_path(self):
        cat = self.category.title
        tmp = self.category
        path_ls = [tmp, ]
        while tmp.parent is not None:
            tmp = tmp.parent
            path_ls.append(tmp)
        return path_ls

    def as_dict(self):
        d = {
            'slug': self.slug,
            'title': self.title,
            'price': self.get_price_with_discount,
        }
        return d

    def save(self, *args, **kwargs):
        if not self.id or not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ('title', 'price')
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def get_photo_url(self):
        if self.photo and hasattr(self.photo, 'url'):
            return self.photo.url
        return '/media/items/no_image.png'

    def photo_tag(self):
        return mark_safe(f'<img src="{self.get_photo_url()}" width="50" height="50" style="object-fit: cover;"/>')
        # return self.photo_url

    def get_favorite_count(self):
        return Favorite.objects.filter(item=self).count()

    def get_detail_url(self):
        return reverse('item_detail_url', kwargs={'slug': self.slug})

    @staticmethod
    def get_price(price):
        kop = int((round(price, 2) - int(price)) * 100)
        return f'{int(price)}{"," + str(kop) if kop else ""} руб.'

    @property
    def get_raw_price(self):
        return self.get_price(self.price)

    @property
    def get_price_with_discount(self):
        if discount := self.discount():
            price_with_discount = self.price - self.price / 100 * discount.value
        else:
            price_with_discount = self.price
        return self.get_price(price_with_discount)

    @property
    def get_raw_price_with_discount(self):
        """
        Функция возвращает цену со скидкой в формате float
        :return: Float
        """
        if discount := self.discount():
            price_with_discount = self.price - self.price / 100 * discount.value
        else:
            price_with_discount = self.price
        return price_with_discount

    def discount(self):
        """
        Находим скидки на эту дату и применяем самую большую
        :return: int
        """
        discounts = Discount.objects.filter(item=self, expire_date__gte=datetime.date.today(),
                                            start_date__lte=datetime.date.today())
        if not discounts:
            return None
        # disc = discounts[0].value
        return discounts[0]

    @property
    def get_rating(self):
        rates = ItemRating.objects.filter(item=self)
        if not len(rates):
            return 0
        # print(rates)
        return sum([int(r.rating) for r in rates]) / len(rates)

    def get_rating_count(self):
        return ItemRating.objects.filter(item=self).count()


class Category(models.Model):
    title = models.CharField(max_length=50)
    parent = models.ForeignKey(
        'Category', on_delete=models.SET_NULL, null=True, blank=True)
    item_spec = models.ManyToManyField('SpecItem', related_name='item_cat', blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Категория товаров'
        verbose_name_plural = 'Категории товаров'


class SpecItem(models.Model):
    """
    Характеристики товара
    """
    item = models.ForeignKey('Item', on_delete=models.CASCADE, null=True, related_name='specs')
    title = models.CharField(max_length=200, verbose_name='Наименование арактеристики, (и единица измерения)')
    value = models.ForeignKey('SpecValue', verbose_name='Значение характеристики', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.title} - {self.value}'

    class Meta:
        verbose_name = 'Характеристика'
        verbose_name_plural = 'Характеристики товара'
        unique_together = ('title', 'value')


class SpecValue(models.Model):
    """
    Занчение характеристики
    """
    value = models.CharField(max_length=50)

    def __str__(self):
        return self.value

    class Meta:
        verbose_name = "Значение характеристики"
        verbose_name_plural = "Значения характеристик"


class Discount(models.Model):
    item = models.ForeignKey('Item', on_delete=models.CASCADE)
    value = models.IntegerField(default=0)
    start_date = models.DateField()
    expire_date = models.DateField()

    def __str__(self):
        return f'Скидка на {self.item.title} {self.value}% действует до {self.expire_date}'

    class Meta:
        verbose_name = 'Скидка'
        verbose_name_plural = 'Скидки'
        ordering = ('expire_date', 'item')
        unique_together = ('item', 'expire_date')


class ItemRating(models.Model):
    """
    Отценки поставленные пользотвалем книге
    """
    item = models.ForeignKey('Item', on_delete=models.CASCADE, related_name='item_rating')
    body = models.TextField(verbose_name='Описание', null=True, blank=True)
    RATING = (
        ('5', 5),
        ('4', 4),
        ('3', 3),
        ('2', 2),
        ('1', 1),
    )
    rating = models.CharField(max_length=1, choices=RATING, verbose_name="Мнение пользователя о книге", default='5')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.item} {self.rating} {self.user}'

    class Meta:
        verbose_name_plural = 'Отценки пользователей'
        verbose_name = 'Отценка пользователя'
        ordering = ('item', 'rating')
        unique_together = ('item', 'user')

    def items_list(self):
        rew_all_sum = ItemRating.objects.aggregate(models.Sum('rating')).values()[0]
        rew_all_count = ItemRating.objects.filter(item__id=self.kwargs['id']).count()


class Favorite(models.Model):
    item = models.ForeignKey('Item', on_delete=models.CASCADE, related_name='favorite')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    create_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'Пользователь {self.user} добавил в избранное {self.item}'

    class Meta:
        verbose_name = 'Предмет помещенный в избранное'
        verbose_name_plural = 'Избранное'
        ordering = ('item', 'create_date')
        unique_together = ('user', 'item')


class Cart(models.Model):
    owner = models.OneToOneField('account.Profile', on_delete=models.CASCADE, unique=True)

    def __str__(self):
        return f"Корзина {self.owner.username}"

    class Meta:
        verbose_name_plural = "Корзины"
        verbose_name = "Корзина"


class CartItems(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='cart_item', null=True)
    item = models.OneToOneField('Item', on_delete=models.CASCADE)
    price_on_order_date = models.FloatField()
    quantity = models.FloatField(default=1)

    def __str__(self):
        return f"{self.order.customer} {self.item} {self.price_on_order_date}"

    class Meta:
        verbose_name = 'Продукт из корзины'
        verbose_name_plural = 'Продукты находящиеся в корзинах'


class Order(models.Model):
    customer = models.OneToOneField('account.Profile', verbose_name="Заказчик", on_delete=models.CASCADE,
                                    related_name="order")
    created = models.DateTimeField(verbose_name="Созадана", auto_now_add=True)
    updated = models.DateTimeField(verbose_name="Обновлен", auto_now=True)
    ordered = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created']
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f'Заказ: {self.id} от {self.created}'

    def sum_order_price(self):
        cart_items = self.cart_item.all()
        return sum([item.price_on_order_date for item in cart_items])

    def sum_order_price_with_discount(self):
        cart_items = self.cart_item.all()
        return sum([item.price_on_order_date - item.price_on_order_date/item.item.discount()*100 for item in cart_items])
# class OrderStatus(models.Model):
#     pass
#
#
# class OrderItem(models.Model):
#     pass
