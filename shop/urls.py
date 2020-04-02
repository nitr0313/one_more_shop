from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from .views import *


urlpatterns = [
    path('', home_page, name='home'),
    path('item/<str:slug>/', ItemDetail.as_view(), name='item_detail_url')
    # path('', include('django.contrib.auth.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
