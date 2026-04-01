from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OffreServiceViewSet, generer_offre_service

router = DefaultRouter()
router.register(r'offres', OffreServiceViewSet, basename='offre')

urlpatterns = [
    # ✅ generer/ AVANT le router pour eviter le conflit pk="generer"
    path('offres/generer/', generer_offre_service, name='generer-offre'),
    path('', include(router.urls)),
]