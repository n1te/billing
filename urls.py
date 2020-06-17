from django.urls import path, include

urlpatterns = [
    path('api/wallets/', include('wallet.api.urls')),
]
