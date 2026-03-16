from django.contrib import admin
from .models import BonCommande, LigneBonCommande

class LigneBonCommandeInline(admin.TabularInline):
    model = LigneBonCommande
    extra = 1

@admin.register(BonCommande)
class BonCommandeAdmin(admin.ModelAdmin):
    list_display  = ['numero', 'fournisseur_nom', 'statut', 'total_net', 'date_commande']
    search_fields = ['numero', 'fournisseur_nom']
    list_filter   = ['statut']
    inlines       = [LigneBonCommandeInline]