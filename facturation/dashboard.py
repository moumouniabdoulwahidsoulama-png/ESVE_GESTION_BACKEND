from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import Facture


def get_dashboard_stats():
    aujourd_hui = timezone.now().date()
    debut_mois  = aujourd_hui.replace(day=1)
    debut_annee = aujourd_hui.replace(month=1, day=1)

    # ===== FACTURES =====
    total_factures      = Facture.objects.filter(type_doc='FACTURE').count()
    factures_ce_mois    = Facture.objects.filter(
                            type_doc='FACTURE',
                            date_creation__gte=debut_mois
                          ).count()

    # ===== PROFORMAS =====
    total_proformas     = Facture.objects.filter(type_doc='PROFORMA').count()
    proformas_en_attente = Facture.objects.filter(
                            type_doc='PROFORMA',
                            statut='BROUILLON'
                          ).count()

    # ===== CHIFFRE D'AFFAIRES =====
    ca_total            = Facture.objects.filter(
                            type_doc='FACTURE'
                          ).aggregate(total=Sum('total_net'))['total'] or 0

    ca_ce_mois          = Facture.objects.filter(
                            type_doc='FACTURE',
                            date_creation__gte=debut_mois
                          ).aggregate(total=Sum('total_net'))['total'] or 0

    ca_cette_annee      = Facture.objects.filter(
                            type_doc='FACTURE',
                            date_creation__gte=debut_annee
                          ).aggregate(total=Sum('total_net'))['total'] or 0

    # ===== FACTURES PAR STATUT =====
    par_statut          = Facture.objects.filter(
                            type_doc='FACTURE'
                          ).values('statut').annotate(count=Count('id'))

    # ===== EVOLUTION MENSUELLE (6 derniers mois) =====
    evolution = []
    for i in range(5, -1, -1):
        date_ref    = aujourd_hui - timedelta(days=30*i)
        debut       = date_ref.replace(day=1)
        if debut.month == 12:
            fin     = debut.replace(year=debut.year+1, month=1, day=1)
        else:
            fin     = debut.replace(month=debut.month+1, day=1)

        montant     = Facture.objects.filter(
                        type_doc='FACTURE',
                        date_creation__gte=debut,
                        date_creation__lt=fin
                      ).aggregate(total=Sum('total_net'))['total'] or 0

        evolution.append({
            'mois':    debut.strftime('%b %Y'),
            'montant': float(montant)
        })

    # ===== TOP 5 CLIENTS =====
    top_clients         = Facture.objects.filter(
                            type_doc='FACTURE'
                          ).values(
                            'client__nom_entreprise'
                          ).annotate(
                            total=Sum('total_net'),
                            nb_factures=Count('id')
                          ).order_by('-total')[:5]

    return {
        'factures': {
            'total':        total_factures,
            'ce_mois':      factures_ce_mois,
        },
        'proformas': {
            'total':        total_proformas,
            'en_attente':   proformas_en_attente,
        },
        'chiffre_affaires': {
            'total':        float(ca_total),
            'ce_mois':      float(ca_ce_mois),
            'cette_annee':  float(ca_cette_annee),
        },
        'par_statut':       list(par_statut),
        'evolution_mensuelle': evolution,
        'top_clients':      list(top_clients),
    }