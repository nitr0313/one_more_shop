from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from .views import *


urlpatterns = [
    path('', ItemsList.as_view(), name='home'),
    path('favorites/', FavoritesItems.as_view(), name='favorites'),
    path('item/<str:slug>/', ItemDetail.as_view(), name='item_detail_url'),
    path('add_to_fav/', add_to_favorites, name='add_to_favorites'),
    path('remove_fav/', remove_from_favorites, name='remove_from_favorites'),
    path('v1/api/favorites/', favorites_api, name='api'),
    path('cart/', cart, name='cart'),
    path('cart_clear/', cart_clear, name='cart_clear'),
    path('add_to_cart/', add_to_cart, name='add_to_cart'),
    path('remove_from_cart/', remove_from_cart, name='remove_from_cart'),
    path('v1/api/cart/', cart_api),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
