from django.contrib import admin
from django.urls import path
from venomconnect.views import connect_wallets_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path('connect/', connect_wallets_view, name='connect_wallets'),
]
