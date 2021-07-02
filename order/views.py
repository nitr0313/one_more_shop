from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic.detail import DetailView
from django.views.generic import CreateView
from django.views.generic.list import ListView
from .models import OrderItems, Order
from account.models import Profile
from shop.cart import Cart
from typing import *
# Create your views here.




class CreateOrder(CreateView):
    model = Order

    def get(self, *args, **kwargs):
        cart = Cart(self.request)
        if len(cart) < 1:
            return redirect('cart')
        profile = Profile.objects.get(user=self.request.user)
        new_order = Order(
            customer=profile,
            status=0
        )
        new_order.save()
        # new_order.save()
        for item in cart:
            print(item)
            ordered_item = OrderItems(
                order=new_order,
                item=item['item'],
                price_on_order_date=item['item'].get_raw_price_with_discount,
                quantity=item['quantity']
                )
            ordered_item.save()
        # new_order.save()
        cart.clear()
        return redirect('orders')


    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        return super().get_context_data(**kwargs)

class OrdersList(ListView):
    model = Order

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context= super().get_context_data(**kwargs)
        profile = get_object_or_404(Profile, user=self.request.user)
        orders = Order.objects.filter(customer=profile)
        order_items = dict()
        for order in orders:
            order_items[order] = OrderItems.objects.filter(order=order.id),
        context['order_items'] = order_items
        return context