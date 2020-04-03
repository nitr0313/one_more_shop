from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from .views import *


urlpatterns = [
    path('', home_page, name='home'),
    path('favorites/', user_favorites, name='favorites'),
    path('item/<str:slug>/', ItemDetail.as_view(), name='item_detail_url'),
    path('add_to_fav/', add_to_favorites, name='add_to_favorites'),
    path('remove_fav/', remove_from_favorites, name='remove_from_favorites'),
    path('v1/api/', favorites_api, name='api')
    # path('', include('django.contrib.auth.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
