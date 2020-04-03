from django.contrib.auth import get_user_model
from django.db import models
# from django.utils.text import slugify
from pytils.translit import slugify
from django.utils.safestring import mark_safe
from django.urls.base import reverse


User = get_user_model()


class Item(models.Model):
    slug = models.SlugField(unique=True, verbose_name='URL', allow_unicode=True, blank=True)
    title = models.CharField(max_length=150, unique=True, verbose_name="Название")
    description = models.TextField(max_length=1000, verbose_name="Описание", blank=True, default="")
    price = models.FloatField(verbose_name="Цена", default=0.0)
    photo = models.ImageField(verbose_name="Фото", upload_to='items/%Y/%m/%d', blank=True)
    in_stock = models.BooleanField(verbose_name='В продаже', default=True)
    on_delete = models.BooleanField(verbose_name='Пометить на удаление', default=False)
    # rating = models.FloatField(verbose_name="Рейтинг", default=0.0)
    discount = models.IntegerField(default=0)
    detail_url = 'item_detail_url'

    def __str__(self):
        return f'{self.id} {self.title} {self.price}'
    
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
        return mark_safe(f'<img src="/{self.get_photo_url()}" width="50" height="50" style="object-fit: cover;"/>')
        # return self.photo_url

    def get_favorite_count(self):
        return Favorite.objects.filter(item=self).count()
    
    def get_detail_url(self):
        return reverse('item_detail_url', kwargs={'slug': self.slug})

    # def get_absolute_url(self):
    #     return redirect(self.slug)

    @property
    def get_price(self):
        price_with_discount = self.price - self.price / 100 * self.discount
        return f'{price_with_discount} р.'

    @property
    def get_rating(self):
        rates = ItemRating.objects.filter(item=self)
        if not len(rates):
            return 0
        # print(rates)
        return sum([int(r.rating) for r in rates]) / len(rates)

    def get_rating_count(self):
        return ItemRating.objects.filter(item=self).count()


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


class Order(models.Model):
    customer = models.OneToOneField('account.Profile', verbose_name="Заказчик", on_delete=models.CASCADE,
                                    related_name="order")
    created = models.DateTimeField(verbose_name="Созадана", auto_now_add=True)
    updated = models.DateTimeField(verbose_name="Обновлен", auto_now=True)

    class Meta:
        ordering = ['-created']
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f'Заказ: {self.id} от {self.created}'

# class OrderStatus(models.Model):
#     pass
#
#
# class OrderItem(models.Model):
#     pass
