from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OffreServiceViewSet, generer_offre_pdf

router = DefaultRouter()
router.register(r'offres', OffreServiceViewSet, basename='offre')

urlpatterns = [
    path('', include(router.urls)),
    # ✅ URL dédiée pour génération PDF sans sauvegarde
    # Utilise "generer-pdf" au lieu de "generer" pour éviter le conflit avec le router DRF
    path('offres/generer-pdf/', generer_offre_pdf, name='offre-generer-pdf'),
]