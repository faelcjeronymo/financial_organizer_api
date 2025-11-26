from django.urls import include, path
from rest_framework import routers

from api.views import BankViewSet, TransactionViewSet

router = routers.DefaultRouter()
router.register(r'transactions', TransactionViewSet)
router.register(r'banks', BankViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

