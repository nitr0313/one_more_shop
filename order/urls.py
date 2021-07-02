from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from .views import OrdersList, CreateOrder


urlpatterns = [
    path('orders/', OrdersList.as_view(), name='orders'),  # TESTCreateOrder
    path('create_order/', CreateOrder.as_view(), name='create_order'),  # TEST
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)