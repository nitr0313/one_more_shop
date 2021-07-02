from django.contrib import admin
from django.contrib.admin import register

# Register your models here.
from .models import Order, OrderItems

admin.site.register(OrderItems)


class OrderItemsLine(admin.TabularInline):
    model = OrderItems
    raw_id_fields = ['item']


@register(Order)
class OrderAdmin(admin.ModelAdmin):
    fields = ('customer','status')
    inlines = [OrderItemsLine]

    class Meta:
        model = Order