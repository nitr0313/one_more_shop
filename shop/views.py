from django.db import models
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import View

from .models import Item


# Create your views here.


def home_page(request):
    items = Item.objects.all().annotate(avg_review=models.Avg('item_rating__rating')).order_by('-avg_review')
    # for item in items:
    #     item.rating = item.get_rating
    #
    # items = items.order_by()
    # for item in items:
    #     print(item, item.get_rating)
    return render(request, 'shop/index.html', {'items': items})


def add_to_favorites(request):
    pass


def remove_from_favorites(request):
    pass


class ItemDetail(View):
    model = Item
    template = 'shop/item_detail.html'

    def get(self, request, slug):
        obj = get_object_or_404(self.model, slug__iexact=slug)
        con = dict(
            admin_object=obj,
            detail=True,
        )
        return render(request, self.template, context=con)
                      # context={self.model.__name__.lower(): obj, 'admin_object': obj, 'detail': True})



