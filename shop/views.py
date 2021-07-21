import os
from shop.services import create_categores, create_items, create_specs, set_analogs_and_related
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import models
from django.http import JsonResponse, request
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView 
from django.db.models import Q
from django.contrib import messages
from .forms import CartAddItemForm
from .cart import Cart
from .models import Category, Item, Favorite, ItemRating, SpecItem, SpecValue, User
from account.models import Profile
from typing import *
from decimal import Decimal
from .utils import Group, XmlParserPRODAT, download_image


# Create your views here.


class HomePage(View):
    ...

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cats = Category.objects.all()
        return context
    


class ItemsList(ListView):
    model = Item
    paginate_by = 12
    context_object_name = 'items'
    queryset = model.objects.all()
    #.annotate(avg_review=models.Avg('item_rating__rating')).order_by('-avg_review')

    def get_queryset(self):
        if 'search' in self.request.GET:
            search_query = self.request.GET.get('search', False)
            return Item.objects.all().filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__title=search_query),
            )
            #.annotate(avg_review=models.Avg('item_rating__rating')).order_by('-avg_review')
        elif 'cat_code' in self.request.GET:
            category = self.request.GET.get('cat_code', False)
            print(category)
            qs = Item.objects.all().filter(category__code=category
                )
                #.annotate(avg_review=models.Avg('item_rating__rating')).order_by('-avg_review')
            if qs:
                return qs
            qs = Item.objects.filter(category__parent__code=category)
            return qs

        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context = dict()
        search_query = self.request.GET.get('search', False)

        # if search_query:
        #     items = Item.objects.all().filter(
        #         Q(title__icontains=search_query) |
        #         Q(description__icontains=search_query) |
        #         Q(category__title=search_query),
        #     ).annotate(avg_review=models.Avg('item_rating__rating')).order_by(
        #         '-avg_review')
        #     context['items'] = items
        #     context['is_paginated'] = False
            
        context['section'] = 'home_page'
        context['nodes'] = Category.objects.all()
        # print(context)
        return context


class FavoritesItems(ListView, LoginRequiredMixin):
    model = Item
    context_object_name = 'items'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = Item.objects.all().annotate(avg_review=models.Avg('item_rating__rating')).order_by(
        '-avg_review').filter(favorite__user=self.request.user)
        context.update(dict(items=items, section='favorites'))
        return context


class ItemDetail(DetailView):
    model = Item
    # template = 'shop/item_detail.html'
    # context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = ItemRating.objects.filter(item=context['object'])
        context['specs'] = SpecValue.objects.filter(item=context['object']).select_related('spec_item')
        context['section'] = 'detail'
        print(context)
        return context


class CategoryList(View):
    model = Category
    context_object_name = 'node'
    template = 'shop/category_list.html'

    def get(self, request, *args, **kwargs):
        cat = get_object_or_404(Category, code=kwargs['code'])
        chield_categories = cat.get_descendants(include_self=True)
        nodes = Category.objects.filter(parent__in=chield_categories)
        print(nodes)
        context = dict(
            cat=cat,
            nodes=nodes
            )
        return render(request=request, template_name=self.template, context=context)

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


@login_required()
@require_POST
def add_to_cart(request):
    cart = Cart(request)
    if not request.is_ajax():
        id = request.POST.get("id")
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
            'cart_count': len(cart),
        }
        # request.session.modified = True
        # return render(request, 'shop/cart.html', {})
        return JsonResponse(data)

    return redirect(request.POST.get('url_from'))


@login_required
def cart(request):
    cart = Cart(request)
    full_price = Decimal()
    for item in cart:
        print(item)
        item['update_quantity_form'] = CartAddItemForm(
            initial={
                'quantity': item['quantity'],
                'update': True
            }
        )
        full_price += int(item['quantity']) * item["item"].get_raw_price_with_discount
        print(item)
    # test_item = Item.objects.all().filter(id=4)[0]
    con = dict(
        cart=cart,
        section='cart',
        full_coast=full_price,
        # test_item=test_item,
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
    """[summary]

    Args:
        request ([type]): [description]

    Returns:
        [type]: [description]
    """    
    cart = Cart(request)
    data = []
    for item in cart:
        tmp = dict(
            id=item['item'].id,
            quantity=item['quantity']
        )
        data.append(tmp)

    return JsonResponse(data, safe=False)


class UpdateDb(View):
    context = dict()
    template = 'shop/update_db.html'

    def get(self, request):        
        self.context['section'] = 'update_db'
        return render(request, self.template, context=self.context)
    
    def post(self, request, *args, **kwargs):
        file_name = request.FILES.get('items_db', False)
        if not file_name:
            return redirect('home')
        # fl_xml = 'trash_data\data\data_lite.xml'
        parser = XmlParserPRODAT(file_name=file_name)
        print('Запуск парсера', file_name)
        parser.run()
        result = parser.get_items()
        groups = parser.get_groups()
        specs = parser.get_features()
        print(f'Результат работы парсера {len(result)=}')
        create_categores(groups)
        create_specs(specs)
        create_items(result)
        set_analogs_and_related(result)
        return redirect('home')


def update_db(request):
    """Обновление товаров базе данных из файла PRODAT.xml
       Returns:
        [type]: [description]
    """
    # if not request.user.is_stuff():
    #     messages.error(request, 'НЕТ ПРАВ')
    #     return redirect('home')

    fl_xml = 'trash_data\data\data.xml'
    parser = XmlParserPRODAT(file_name=fl_xml)
    parser.run()
    result = parser.get_items()
    groups = parser.get_groups()
    specs = parser.get_features()

    create_categores(groups)
    create_specs(specs)
    create_items(result)
    set_analogs_and_related(result)
    return redirect('home')
        
    