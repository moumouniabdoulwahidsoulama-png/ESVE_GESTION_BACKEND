from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse
from .models import Facture, LigneFacture
from .serializers import FactureSerializer, FactureCreateSerializer, LigneFactureSerializer
from .pdf_generator import generer_pdf_facture
# Ajoute cet import en haut
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .dashboard import get_dashboard_stats


class FactureViewSet(viewsets.ModelViewSet):
    queryset           = Facture.objects.all().select_related('client')
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['type_doc', 'statut', 'client']
    search_fields      = ['numero', 'client__nom_entreprise']
    ordering_fields    = ['date_creation', 'total_net']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return FactureCreateSerializer
        return FactureSerializer

    @action(detail=True, methods=['post'])
    def valider(self, request, pk=None):
        """Convertit une proforma en facture définitive."""
        proforma = self.get_object()

        if proforma.type_doc != 'PROFORMA':
            return Response(
                {'error': 'Ce document est déjà une facture définitive.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if proforma.statut == 'ANNULE':
            return Response(
                {'error': 'Impossible de valider une proforma annulée.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Créer la facture définitive
        facture = Facture.objects.create(
            client              = proforma.client,
            type_doc            = 'FACTURE',
            statut              = 'ENVOYE',
            proforma_origine    = proforma,
            validite_jours      = proforma.validite_jours,
            remise_pct          = proforma.remise_pct,
            notes               = proforma.notes,
            total_ht_brut       = proforma.total_ht_brut,
            montant_remise      = proforma.montant_remise,
            total_ht            = proforma.total_ht,
            tva_18pct           = proforma.tva_18pct,
            retenue_5pct        = proforma.retenue_5pct,
            bic_2pct            = proforma.bic_2pct,
            total_net           = proforma.total_net,
        )

        # Générer le numéro
        facture.generer_numero()

        # Copier les lignes
        for ligne in proforma.lignes.all():
            LigneFacture.objects.create(
                facture               = facture,
                description           = ligne.description,
                reference_client      = ligne.reference_client,
                reference_fournisseur = ligne.reference_fournisseur,
                prix_unitaire_ht      = ligne.prix_unitaire_ht,
                quantite              = ligne.quantite,
                total_ht              = ligne.total_ht,
                delais                = ligne.delais,
                ordre                 = ligne.ordre,
            )

        # Marquer la proforma comme validée
        proforma.statut = 'VALIDE'
        proforma.save(update_fields=['statut'])

        # Générer le PDF automatiquement
        try:
            generer_pdf_facture(facture)
        except Exception as e:
            print(f"Erreur PDF : {e}")

        return Response(
            FactureSerializer(facture).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def generer_pdf(self, request, pk=None):
        """Génère ou régénère le PDF d'une facture."""
        facture = self.get_object()
        try:
            generer_pdf_facture(facture)
            return Response(
                {'success': f'PDF généré : {facture.numero}.pdf'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def pdf(self, request, pk=None):
        """Télécharge le PDF de la facture."""
        facture = self.get_object()

        if not facture.pdf_file:
            # Générer automatiquement si pas encore fait
            try:
                generer_pdf_facture(facture)
            except Exception as e:
                return Response(
                    {'error': f'Impossible de générer le PDF : {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        response = FileResponse(
            facture.pdf_file.open('rb'),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="{facture.numero}.pdf"'
        return response


class LigneFactureViewSet(viewsets.ModelViewSet):
    queryset           = LigneFacture.objects.all()
    serializer_class   = LigneFactureSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend]
    filterset_fields   = ['facture']


    # Ajoute cette vue à la fin du fichier
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Retourne les statistiques pour le tableau de bord."""
    stats = get_dashboard_stats()
    return Response(stats)