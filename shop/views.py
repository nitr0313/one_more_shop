from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.base import View

from .models import Item, Favorite, ItemRating, SpecItem


# Create your views here.


def home_page(request):
    if request.method == 'POST':
        print(request.POST)
    else:
        print(request.GET)
    items = Item.objects.all().annotate(avg_review=models.Avg('item_rating__rating')).order_by(
        '-avg_review')
    top_items = items[0:3]
    con = dict(
        section='home_page',
        items=items,
        top_items=top_items,
    )

    return render(request, 'shop/index.html', context=con)


def user_favorites(request):
    items = Item.objects.all().annotate(avg_review=models.Avg('item_rating__rating')).order_by(
        '-avg_review').filter(favorite__user=request.user)
    section = 'favorites'
    return render(request, 'shop/index.html', {'items': items, 'section': section})


class ItemDetail(View):
    model = Item
    template = 'shop/item_detail.html'

    def get(self, request, slug):
        item = get_object_or_404(self.model, slug__iexact=slug)
        comments = ItemRating.objects.filter(item__slug=slug)
        specs = SpecItem.objects.filter(item__slug=slug)
        con = dict(
            item=item,
            comments=comments,
            detail=True,
            specs=specs,
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


@login_required()
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


@login_required()
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


def add_to_cart(request):
    if request.method == 'POST':
        if not request.session.get('cart'):
            request.session['cart'] = list()
        else:
            request.session['cart'] = list(request.session['cart'])
        item_id = request.POST.get('id')
        item_exist = next((item for item in request.session['cart'] if item['id'] == item_id), False)

        add_data = {
            'id': item_id,
            'item': Item.objects.get(id=item_id).as_dict()
        }

        if not item_exist:
            request.session['cart'].append(add_data)
            request.session.modified = True

    if request.is_ajax():
        item_id = request.POST.get('id')

        data = {
            'id': item_id,
            'item': Item.objects.get(id=item_id).as_dict()
        }
        request.session.modified = True
        return JsonResponse(data)

    return redirect(request.POST.get('url_from'))


def cart(request):
    if request.method == 'GET':
        cart = request.session.get('cart', False)
        id_list = []
        sum_price_items = 0
        if cart:
            for item in cart:
                id_list.append(item['id'])
                sum_price_items += float(item['item']['price'].split(' ')[0])

        items = Item.objects.filter(id__in=id_list)
        # sum_price_items = items.aggregate(models.Sum('get_price_with_discount'))
        # print(items)
        con = dict(
            cart=items,
            section='cart'
        )
        return render(request, 'shop/cart.html', context=con)

    pass


def remove_from_cart(request):
    if request.method == 'POST':
        item_id = request.POST.get('id')
        for item in request.session['cart']:
            if item[id] == item_id:
                item.clear()
        while {} in request.session['cart']:
            request.session['cart'].remove({})

        if not request.session['cart']:
            del request.session['cart']

    if request.is_ajax():
        item_id = request.POST.get('id')
        data = {
            'id': item_id,
            'item': Item.objects.get(id=item_id).as_dict()
        }
        request.session.modified = True
        return JsonResponse(data)

    return redirect(request.POST.get('url_from'))


@login_required()
def cart_api(request):
    if request.user.is_active and 'cart' in request.session:
        user_cart = request.session['cart']
    else:
        user_cart = []
    # items = Item.objects.filter(on_delete=False)
    # print(all_favorites.count())

    data = []
    for item in user_cart:
        print(item)
        tmp = dict(
            id=item['id'],
            item=item
        )
        data.append(tmp)

    return JsonResponse(data, safe=False)
