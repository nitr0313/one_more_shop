from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import models
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.base import View
from django.db.models import Q
from .forms import CartAddItemForm
from .cart import Cart
from .models import Item, Favorite, ItemRating, SpecItem


# Create your views here.


def home_page(request):
    if request.method == 'GET':
        search_query = request.GET.get('search', False)

    if search_query:
        items = Item.objects.all().filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
            # Q(category__title__item=search_query),
        ).annotate(avg_review=models.Avg('item_rating__rating')).order_by(
            '-avg_review')
    else:
        items = Item.objects.all().annotate(avg_review=models.Avg('item_rating__rating')).order_by(
            '-avg_review')
    top_items = items[0:3]
    con = dict(
        section='home_page',
        items=items,
        top_items=top_items,
    )
    # TODO Реализовать выбор шаблона из сессии пользователя
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

        # print(add_data)
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


@login_required()  # TODO: Переделать так что бы перекидывало на логин при попытке добавить в корзину
@require_POST
def add_to_cart(request):
    cart = Cart(request)
    print(request.POST)
    if not request.is_ajax():
        item = get_object_or_404(Item, id=id)
        print(item)
        form = CartAddItemForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            cart.add(item=item,
                     quantity=cd['quantity'],
                     update_quantity=cd['update']
                     )
    else:
        item_id = int(request.POST.get('id'))
        item_quantity = int(request.POST.get('quantity'))
        update_quantity = bool(int(request.POST.get('update_quantity', False)))
        print(f'{item_id=} {item_quantity=} {type(item_quantity)=} {update_quantity=}')
        cart.add(item=get_object_or_404(Item, id=item_id),
                 quantity=item_quantity,
                 update_quantity=update_quantity
                 )
        count = cart.count_items(item_id)

        data = {
            'id': item_id,
            'quantity': count,
        }
        # request.session.modified = True
        # return render(request, 'shop/cart.html', {})
        return JsonResponse(data)

    return redirect(request.POST.get('url_from'))


def cart(request):
    cart = Cart(request)
    for item in cart:
        print(item)
        item['update_quantity_form'] = CartAddItemForm(
            initial={
                'quantity': item['quantity'],
                'update': True
            }
        )
        print(item)

    con = dict(
        cart=cart,
        section='cart'
    )
    return render(request, 'shop/cart.html', context=con)


@login_required()
@require_POST
def remove_from_cart(request):
    if request.method == 'POST':
        cart = Cart(request)
        item_id = request.POST.get('id')
        for item in cart:
            if str(item["item"].id) == item_id:
                cart.remove(item["item"])
                break

    if request.is_ajax():
        item_id = request.POST.get('id')
        data = {
            'id': item_id,
        }
        return JsonResponse(data)

    return redirect(request.POST.get('url_from'))


@login_required
def cart_clear(request):
    # del request.session['cart']
    cart = Cart(request)
    cart.clear()
    return redirect('home')


@login_required()
def cart_api(request):
    cart = Cart(request)
    data = []
    for item in cart:
        tmp = dict(
            id=item['item'].id,
            quantity=item['quantity']
        )
        data.append(tmp)

    return JsonResponse(data, safe=False)
