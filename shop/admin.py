from django.contrib import admin
from django.contrib.admin import register
from django.contrib.admin.options import ModelAdmin
from django.db.models.base import Model

from .models import Item, ItemRating, Favorite, Category, SpecItem, SpecValue, Discount
from mptt.admin import MPTTModelAdmin
# Register your models here.

admin.site.register(ItemRating)
admin.site.register(Favorite)
# admin.site.register(Category, MPTTModelAdmin)
admin.site.register(SpecValue)
admin.site.register(Discount)


# @register(Category)
# class CategoryAdmin(admin.ModelAdmin):
#     # fields = ('title', 'code', 'parent')
#     list_display = ('title', 'code', 'parent')
#     list_filter = ('parent',)

#     class Meta:
#         model = Category

@register(Category)
class CategoryAdmin(MPTTModelAdmin):
    fields = ('title', 'slug', 'code', 'parent')
    list_display = ('title', 'code', 'parent')
    readonly_fields = ('slug',)


@register(SpecItem)
class SpecItemAdmin(admin.ModelAdmin):
    # fields = ('item', 'title', 'value')
    ordering = ('title',)
    fields = ('code', 'title', 'uom')
    search_fields = ('code', 'title')

    class Meta:
        model = SpecItem


# class SpecItemInLine(admin.TabularInline):
#     model = SpecItem
#     raw_id_field = ['code', 'title']


class ItemRatingInLine(admin.TabularInline):
    model = ItemRating
    raw_id_field = ['item']

# class CategoryInLine(admin.TabularInline):
#     model = Category
#     raw_id_field = ['item']

# @register(SpecValue)
class SpecValueInLine(admin.TabularInline):
    model = SpecValue
    raw_id_fields = ['item', 'spec_item']


@register(Item)
class ItemAdmin(admin.ModelAdmin):
    fields = ('photo_tag', 'slug', 'photo',
    'brand', 'category', 'title', 'description',
    'quantity_unit', 'quantity_min','price', 'base_price',
    'in_stock', 'on_delete', 'analogs',
    'related')
    list_display = ('photo_tag', 'slug', 'title', 'quantity_unit', 'price', 'in_stock', 'on_delete')
    readonly_fields = ['photo_tag', 'slug']
    inlines = [SpecValueInLine, ItemRatingInLine]
    search_fields = ('title',)

    class Meta:
        model = Item

# admin.site.register(Item)
