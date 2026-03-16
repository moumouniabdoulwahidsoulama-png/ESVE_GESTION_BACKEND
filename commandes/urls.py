from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BonCommandeViewSet, LigneBonCommandeViewSet

router = DefaultRouter()
router.register(r'commandes', BonCommandeViewSet, basename='bon-commande')
router.register(r'lignes',    LigneBonCommandeViewSet, basename='ligne-commande')

urlpatterns = [
    path('', include(router.urls)),
]