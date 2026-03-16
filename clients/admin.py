from django.contrib import admin
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display  = ['nom_entreprise', 'contact_nom', 'telephone', 'email', 'actif']
    search_fields = ['nom_entreprise', 'contact_nom', 'ifu', 'rccm']
    list_filter   = ['actif', 'regime_imposition']