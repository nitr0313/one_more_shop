from django.contrib import admin
from django.contrib.admin import register

from .models import Item, ItemRating, Favorite, Order

# Register your models here.

admin.site.register(ItemRating)
admin.site.register(Favorite)
admin.site.register(Order)


@register(Item)
class ItemAdmin(admin.ModelAdmin):
    fields = ('photo_tag', 'slug', 'title', 'description', 'price', 'discount', 'in_stock', 'on_delete')
    list_display = ('photo_tag', 'slug', 'title', 'price', 'discount', 'in_stock', 'on_delete')
    readonly_fields = ['photo_tag']

    class Meta:
        model = Item


# admin.site.register(Item)
