from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path('', include('shop.urls')),
    path('order/', include('order.urls')),
    path('lk/', include('account.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ModuleNotFoundError:
        pass
