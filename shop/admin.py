from django.contrib import admin
from django.contrib.admin import register

from .models import Item, ItemRating, Favorite, Category, SpecItem, SpecValue, Discount

# Register your models here.

admin.site.register(ItemRating)
admin.site.register(Favorite)
admin.site.register(Category)
admin.site.register(SpecValue)
admin.site.register(Discount)



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


class ItemRatingInLine(admin.TabularInline):
    model = ItemRating
    raw_id_field = ['item']

# class CategoryInLine(admin.TabularInline):
#     model = Category
#     raw_id_field = ['item']


@register(Item)
class ItemAdmin(admin.ModelAdmin):
    fields = ('photo_tag', 'photo', 'slug', 'category', 'title', 'description', 'quantity_unit', 'price', 'in_stock', 'on_delete')
    list_display = ('photo_tag', 'slug', 'title', 'quantity_unit', 'price', 'in_stock', 'on_delete')
    readonly_fields = ['photo_tag']
    inlines = [SpecItemInLine, ItemRatingInLine]

    class Meta:
        model = Item

# admin.site.register(Item)
