import datetime
import json

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.query_utils import Q
from django.utils.safestring import mark_safe
from django.urls.base import reverse
from django.db.models import Sum
from django.utils import timezone

from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
import mptt
from pytils.translit import slugify
from autoslug import AutoSlugField


User = get_user_model()

# UNIT_CHOICE = (
#     ('шт', 'шт'),
#     ('г', 'грамм'),
#     ('кг', 'килограмм'),
#     ('м', 'метр'),
#     ('см', 'сантиметр'),
#     ('мм', 'милиметр'),

# )

UNIT_CHOICE = (
    ('GRM', 'грамм'),
    ('KGM', 'килограмм'),
    ('LTR', 'литр'),
    ('MMT', 'миллиметр'),
    ('MTK', 'квадратный метр'),
    ('MTQ', 'кубический метр'),
    ('MTR', 'метр'),
    ('MGM', 'миллиграмм'),
    ('MLT', 'миллилитр'),
    ('MMQ', 'миллиметр кубический'),
    ('PCE', 'штук'),
    ('DMQ', 'дециметр кубический'),
    ('CMT', 'сантиметр'),
    ('NMP', 'упаковка'),
    ('NBB', 'бобина(бухта)'),
)


class Item(models.Model):
    brand = models.CharField(max_length=250, blank=True, default="")
    code = models.CharField(max_length=10, db_index=True, blank=True)
    slug = AutoSlugField(populate_from='code')
    category = TreeForeignKey('Category', related_name='cat', null=True, blank=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=250, db_index=True, unique=True, verbose_name="Название")
    description = models.TextField(max_length=1000, db_index=True, verbose_name="Описание", blank=True, default="")
    price = models.DecimalField(verbose_name="Цена", max_digits=10,  decimal_places=2)
    base_price = models.DecimalField(verbose_name="Базоваяя цена", max_digits=10,  decimal_places=2)
    photo = models.ImageField(verbose_name="Фото", upload_to='media/items/%Y/%m/%d', blank=True)
    in_stock = models.BooleanField(verbose_name='В продаже', default=True)
    on_delete = models.BooleanField(verbose_name='Пометка на удаление', default=False)
    detail_url = 'item_detail_url'
    quantity_unit = models.CharField(max_length=3, choices=UNIT_CHOICE, default="PCE")
    quantity_min = models.IntegerField(verbose_name="Минимальное количество заказ")
    quantity = models.IntegerField(verbose_name="Остаток на складе", default=0)
    quantity_lots = models.CharField(max_length=250, verbose_name="Остаток на складе: размеры остатков", default='')
    analogs = models.ManyToManyField('Item', verbose_name="Аналоги", related_name='analog')
    related = models.ManyToManyField('Item', verbose_name="Сопутствующие товары", related_name='related_item')

    def __str__(self):
        return f'{self.code} {self.title} {self.price}'

    def get_quantity_lots(self):
        return json.loads(self.quantity_lots)

    def set_quantity_lots(self, obj):
        if obj is None:
            self.quantity_lots = ''
        self.quantity_lots = json.dumps(obj)

    def set_analogs(self, analogs):
        items = Item.objects.filter(code__in=analogs)
        self.analogs.add(*items)
        self.save()

    def set_related(self, related_items):
        items = Item.objects.filter(code__in=related_items)
        self.related.add(*items)
        self.save()

    @property
    def category_path(self):
        cat = self.category
        path_ls = [cat, ]
        while cat.parent is not None:
            cat = cat.parent
            path_ls.append(cat)
        print(path_ls)
        return path_ls[::-1][1:]
    
    def as_dict(self):
        d = {
            'slug': self.slug,
            'title': self.title,
            'price': self.get_price_with_discount,
        }
        return d

    def save(self, *args, **kwargs):
        # if not self.id or not self.slug:
        #     self.slug = slugify(self.code)
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


class Category(MPTTModel):
    title = models.CharField(max_length=150)
    code = models.CharField(max_length=15, unique=True, db_index=True)
    slug = AutoSlugField(populate_from='code', always_update=True, unique=True)
    parent = TreeForeignKey(
        'self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'Категория товаров'
        verbose_name_plural = 'Категории товаров'
    class MPTTMeta:
        level_attr = 'mptt_level'
        order_insertion_by=['title']

    def __str__(self):
        return self.title

# mptt.register(Category, order_insertion_by=['name'])



class SpecItem(models.Model):
    """
    Характеристики товара
    """
    code = models.CharField(max_length=20, verbose_name="Код характеристики", unique=True)
    title = models.CharField(max_length=200, verbose_name='Наименование арактеристики, (и единица измерения)')
    # value = models.ForeignKey('SpecValue', verbose_name='Значение характеристики', on_delete=models.CASCADE, null=True)
    uom = models.CharField(max_length=20, verbose_name='Еденицы измерения', null=True)

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'Характеристика'
        verbose_name_plural = 'Характеристики товара'


class SpecValue(models.Model):
    """
    Занчение характеристики
    """
    item = models.ForeignKey('Item', on_delete=models.CASCADE, related_name='spec_value')
    spec_item = models.ForeignKey('SpecItem', on_delete=models.CASCADE, related_name='value')
    value = models.CharField(max_length=150, verbose_name="Значение характеристики", null=True)

    def __str__(self):
        return self.value

    class Meta:
        verbose_name = "Значение характеристики"
        verbose_name_plural = "Значения характеристик"
        unique_together = ('spec_item', 'item')


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
    Отценки поставленные пользователем
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
    rating = models.CharField(max_length=1, choices=RATING, verbose_name="Мнение пользователя о товаре", default='5')
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
