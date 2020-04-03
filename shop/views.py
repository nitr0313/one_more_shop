from django.db import models
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.base import View

from .models import Item, Favorite, ItemRating

# Create your views here.
DEBAG = False


def home_page(request):
    items = Item.objects.all().annotate(avg_review=models.Avg('item_rating__rating')).order_by(
        '-avg_review')
    return render(request, 'shop/index.html', {'items': items, 'test': DEBAG})


def user_favorites(request):
    items = Item.objects.all().annotate(avg_review=models.Avg('item_rating__rating')).order_by(
        '-avg_review').filter(favorite__user=request.user)
    return render(request, 'shop/index.html', {'items': items, 'test': DEBAG})


class ItemDetail(View):
    model = Item
    template = 'shop/item_detail.html'

    def get(self, request, slug):
        item = get_object_or_404(self.model, slug__iexact=slug)
        comments = ItemRating.objects.filter(item__slug=slug)
        con = dict(
            item=item,
            comments=comments,
            detail=True,
        )
        return render(request, self.template, context=con)
        # context={self.model.__name__.lower(): obj, 'admin_object': obj, 'detail': True})


# Функционал добавление и удаления из избранного
def add_to_favorites(request):
    if request.method == 'POST':
        add_data = {
            'type': request.POST.get('type'),
            'id': request.POST.get('id'),
            # 'user': request.user.username
        }
        user = request.user

        print(add_data)
        if user.is_authenticated and user.is_active:
            if add_data['id'] and not Favorite.objects.filter(user=user, item_id=add_data['id']):
                Favorite.objects.create(user=user, item_id=request.POST.get('id'))
        else:
            message = "Залогиньтесь для добавления в избранное"

    if request.is_ajax():
        print('is ajax')
        data = {
            'type': request.POST.get('type'),
            'id': request.POST.get('id'),
        }
        # request.session.modified = True
        return JsonResponse(data)
    return redirect(request.POST.get('url_from'))


def remove_from_favorites(request):
    if request.method == 'POST':
        id = request.POST.get('id')

        user = request.user
        if user.is_authenticated and user.is_active:
            if id:
                fav_item = Favorite.objects.get(item_id=id, user=user)
                fav_item.delete()
        else:
            message = 'Залогиньтесь для добавления в избранное'

    if request.is_ajax():
        data = {
            'type': request.POST.get('type'),
            'id': request.POST.get('id')
        }
        # request.session.modified = True
        return JsonResponse(data)
    return redirect(request.POST.get('url_from'))


def favorites_api(request):
    # all_favorites = Favorite.objects.all()
    if request.user.is_authenticated and request.user.is_active:
        user_favorites = Favorite.objects.filter(user=request.user)
        user_favorites_list = [fav.item_id for fav in user_favorites]
    else:
        user_favorites_list = []
    items = Item.objects.filter(on_delete=False)
    # print(all_favorites.count())

    data = []
    for item in items:
        tmp = dict(
            type='test1',
            id=item.id,
            count=item.get_favorite_count(),
            user_has=item.id in user_favorites_list,
        )
        data.append(tmp)

    return JsonResponse(data, safe=False)
