from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OffreServiceViewSet, generer_offre_service

router = DefaultRouter()
router.register(r'offres', OffreServiceViewSet, basename='offre')

urlpatterns = [
    path('', include(router.urls)),
    path('offres/generer/', generer_offre_service, name='generer-offre'),
]