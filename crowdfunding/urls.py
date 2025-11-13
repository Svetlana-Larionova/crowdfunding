from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CollectViewSet, PaymentViewSet

router = DefaultRouter()
router.register(r'collects', CollectViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]