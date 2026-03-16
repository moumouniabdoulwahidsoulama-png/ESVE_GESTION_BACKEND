from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse
from .models import BonCommande, LigneBonCommande
from .serializers import BonCommandeSerializer, BonCommandeCreateSerializer, LigneBonCommandeSerializer
from .pdf_generator import generer_pdf_bon_commande


class BonCommandeViewSet(viewsets.ModelViewSet):
    queryset           = BonCommande.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['statut']
    search_fields      = ['numero', 'fournisseur_nom']
    ordering_fields    = ['date_commande', 'total_net']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return BonCommandeCreateSerializer
        return BonCommandeSerializer

    @action(detail=True, methods=['post'])
    def generer_pdf(self, request, pk=None):
        """Génère ou régénère le PDF du bon de commande."""
        bon = self.get_object()
        try:
            generer_pdf_bon_commande(bon)
            return Response(
                {'success': f'PDF généré : {bon.numero}.pdf'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def pdf(self, request, pk=None):
        """Télécharge le PDF du bon de commande."""
        bon = self.get_object()

        if not bon.pdf_file:
            try:
                generer_pdf_bon_commande(bon)
            except Exception as e:
                return Response(
                    {'error': f'Impossible de générer le PDF : {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        response = FileResponse(
            bon.pdf_file.open('rb'),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="{bon.numero}.pdf"'
        return response


class LigneBonCommandeViewSet(viewsets.ModelViewSet):
    queryset           = LigneBonCommande.objects.all()
    serializer_class   = LigneBonCommandeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend]
    filterset_fields   = ['bon_commande']