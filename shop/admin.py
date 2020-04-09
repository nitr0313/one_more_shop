from django.contrib import admin
from django.contrib.admin import register

from .models import Item, ItemRating, Favorite, Order, Category, SpecItem, SpecValue

# Register your models here.

admin.site.register(ItemRating)
admin.site.register(Favorite)
admin.site.register(Order)
admin.site.register(Category)
admin.site.register(SpecValue)


@register(SpecItem)
class SpecItemAdmin(admin.ModelAdmin):
    # fields = ('item', 'title', 'value')
    ordering = ('item', 'title')
    fields = ('item', 'title', 'value')

    class Meta:
        model = SpecItem


class SpecItemInLine(admin.TabularInline):
    model = SpecItem
    raw_id_field = ['item']


@register(Item)
class ItemAdmin(admin.ModelAdmin):
    fields = ('photo_tag', 'slug', 'title', 'description', 'price', 'discount', 'in_stock', 'on_delete')
    list_display = ('photo_tag', 'slug', 'title', 'price', 'discount', 'in_stock', 'on_delete')
    readonly_fields = ['photo_tag']
    inlines = [SpecItemInLine]

    class Meta:
        model = Item

# admin.site.register(Item)
