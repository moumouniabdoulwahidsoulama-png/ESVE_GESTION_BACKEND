from django.contrib import admin
from .models import Profil, DemandeApplication

@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'telephone', 'created_at']
    list_filter  = ['role']

@admin.register(DemandeApplication)
class DemandeApplicationAdmin(admin.ModelAdmin):
    list_display  = ['nom_entreprise', 'nom_contact', 'telephone',
                     'type_application', 'budget', 'statut', 'date_demande']
    list_filter   = ['statut', 'type_application', 'budget']
    search_fields = ['nom_entreprise', 'nom_contact', 'email']
    readonly_fields = ['date_demande', 'date_modification']