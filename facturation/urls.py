from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FactureViewSet, LigneFactureViewSet, dashboard_stats

router = DefaultRouter()
router.register(r'factures', FactureViewSet,      basename='facture')
router.register(r'lignes',   LigneFactureViewSet, basename='ligne-facture')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/stats/', dashboard_stats, name='dashboard-stats'),
]