from django.urls import include, path


urlpatterns = [
    path('api/wallets/', include('wallet.api.urls')),
]
