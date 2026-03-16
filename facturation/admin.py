from django.contrib import admin
from .models import Facture, LigneFacture

class LigneFactureInline(admin.TabularInline):
    model  = LigneFacture
    extra  = 1

@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display  = ['numero', 'client', 'type_doc', 'statut', 'total_net', 'date_creation']
    search_fields = ['numero', 'client__nom_entreprise']
    list_filter   = ['type_doc', 'statut']
    inlines       = [LigneFactureInline]