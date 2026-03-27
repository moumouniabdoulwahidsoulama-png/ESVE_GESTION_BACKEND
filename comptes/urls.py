from django.urls import path
from . import views

urlpatterns = [
    path('register/',              views.RegisterView.as_view(),           name='register'),
    path('me/',                    views.mon_profil,                       name='mon-profil'),
    path('utilisateurs/',          views.liste_utilisateurs,               name='liste-utilisateurs'),
    path('demandes/',              views.DemandeApplicationView.as_view(), name='demande-create'),
    path('demandes/liste/',        views.DemandeApplicationListView.as_view(), name='demande-list'),
    path('demandes/<int:pk>/statut/', views.update_demande_statut,         name='demande-statut'),
    path('utilisateurs/',
         views.liste_utilisateurs,
         name='liste-utilisateurs'),

    path('utilisateurs/<int:pk>/supprimer/',
         views.supprimer_utilisateur,
         name='supprimer-utilisateur'),

    path('utilisateurs/<int:pk>/modifier/',
         views.modifier_utilisateur,
         name='modifier-utilisateur'),
]
