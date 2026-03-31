from django.urls import path
from . import views

urlpatterns = [
    path('offres/generer/', views.generer_offre_service, name='generer-offre'),
]