from rest_framework import viewsets, filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse
from .models import Facture, LigneFacture
from .serializers import FactureSerializer, FactureCreateSerializer, LigneFactureSerializer
from .pdf_generator import generer_pdf_facture
from .dashboard import get_dashboard_stats


class FactureViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['type_doc', 'statut', 'client']
    search_fields      = ['numero', 'client__nom_entreprise']
    ordering_fields    = ['date_creation', 'total_net']

    def get_queryset(self):
        user = self.request.user
        # Corbeille : paramètre ?corbeille=1
        show_deleted = self.request.query_params.get('corbeille', '0') == '1'
        try:
            if user.profil.role == 'CLIENT':
                from clients.models import Client
                try:
                    client = Client.objects.get(email=user.email)
                    return Facture.objects.filter(
                        client=client, is_deleted=show_deleted
                    ).select_related('client')
                except Client.DoesNotExist:
                    return Facture.objects.none()
        except Exception:
            pass
        return Facture.objects.filter(is_deleted=show_deleted).select_related('client')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return FactureCreateSerializer
        return FactureSerializer

    # ✅ Soft delete au lieu de vraiment supprimer
    def destroy(self, request, *args, **kwargs):
        facture = self.get_object()
        # Si cette facture vient d'une proforma, on remet la proforma en BROUILLON
        if facture.proforma_origine:
            try:
                proforma = facture.proforma_origine
                proforma.statut = 'BROUILLON'
                proforma.save(update_fields=['statut'])
            except Exception:
                pass
        facture.soft_delete()
        return Response({'success': 'Facture déplacée dans la corbeille.'},
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='restaurer')
    def restaurer(self, request, pk=None):
        facture = self.get_object()
        facture.restore()
        return Response({'success': f'{facture.numero} restaurée.'})

    @action(detail=True, methods=['delete'], url_path='supprimer_definitif')
    def supprimer_definitif(self, request, pk=None):
        facture = self.get_object()
        if facture.pdf_file:
            facture.pdf_file.delete(save=False)
        facture.delete()
        return Response({'success': 'Supprimée définitivement.'})

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        try:
            facture = self.get_object()
            if facture.pdf_file:
                facture.pdf_file.delete(save=True)
        except Exception:
            pass
        return response

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def valider(self, request, pk=None):
        proforma = self.get_object()
        if proforma.type_doc != 'PROFORMA':
            return Response({'error': 'Ce document est déjà une facture définitive.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if proforma.statut == 'ANNULE':
            return Response({'error': 'Impossible de valider une proforma annulée.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # ✅ Vérifie qu'il n'existe pas déjà une facture active (non supprimée) pour cette proforma
        facture_active = Facture.objects.filter(
            proforma_origine=proforma, is_deleted=False
        ).first()
        if facture_active:
            return Response(
                {'error': f'Une facture existe déjà : {facture_active.numero}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        import uuid
        facture = Facture.objects.create(
            numero              = f"TEMP-{uuid.uuid4().hex[:8].upper()}",
            client              = proforma.client,
            type_doc            = 'FACTURE',
            statut              = 'ENVOYE',
            proforma_origine    = proforma,
            validite_jours      = proforma.validite_jours,
            termes_paiement     = proforma.termes_paiement,
            remise_pct          = proforma.remise_pct,
            notes               = proforma.notes,
            appliquer_remise    = proforma.appliquer_remise,
            appliquer_tva       = proforma.appliquer_tva,
            appliquer_retenue   = proforma.appliquer_retenue,
            appliquer_bic       = proforma.appliquer_bic,
            appliquer_transport = proforma.appliquer_transport,
            montant_transport   = proforma.montant_transport,
            total_ht_brut       = proforma.total_ht_brut,
            montant_remise      = proforma.montant_remise,
            total_ht            = proforma.total_ht,
            tva_18pct           = proforma.tva_18pct,
            retenue_5pct        = proforma.retenue_5pct,
            bic_2pct            = proforma.bic_2pct,
            total_net           = proforma.total_net,
        )
        facture.generer_numero()

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

        proforma.statut = 'VALIDE'
        proforma.save(update_fields=['statut'])

        try:
            generer_pdf_facture(facture)
        except Exception as e:
            print(f"Erreur PDF : {e}")

        return Response(FactureSerializer(facture).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def generer_pdf(self, request, pk=None):
        facture = self.get_object()
        try:
            if facture.pdf_file:
                facture.pdf_file.delete(save=False)
            generer_pdf_facture(facture)
            return Response({'success': f'PDF généré : {facture.numero}.pdf'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    @action(detail=True, methods=['get'])
    def pdf(self, request, pk=None):
        facture = self.get_object()
        try:
            if facture.pdf_file:
                facture.pdf_file.delete(save=False)
            generer_pdf_facture(facture)
            facture.refresh_from_db()
        except Exception as e:
            return Response({'error': f'Impossible de générer le PDF : {str(e)}'}, status=500)
        response = FileResponse(facture.pdf_file.open('rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{facture.numero}.pdf"'
        return response


class LigneFactureViewSet(viewsets.ModelViewSet):
    queryset           = LigneFacture.objects.all()
    serializer_class   = LigneFactureSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend]
    filterset_fields   = ['facture']


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    from .dashboard import get_dashboard_stats
    return Response(get_dashboard_stats())