from rest_framework import routers

from .views import WalletViewSet, TransactionViewSet
from django.urls import path, include


router = routers.SimpleRouter()
router.register('', WalletViewSet)

transaction_router = routers.DefaultRouter()
transaction_router.register('', TransactionViewSet)

urlpatterns = router.urls + [
    path('<wallet_name>/transactions/', include(transaction_router.urls))
]
