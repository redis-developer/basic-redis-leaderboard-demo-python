from django.urls import path
from django.conf.urls import url, include
from django.views.static import serve
from django.conf import settings

urlpatterns = [
    path('', include('core.urls')),
    url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT})
]
