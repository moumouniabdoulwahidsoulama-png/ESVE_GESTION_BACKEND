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
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['statut']
    search_fields      = ['numero', 'fournisseur_nom']
    ordering_fields    = ['date_commande', 'total_net']

    def get_queryset(self):
        user = self.request.user
        show_deleted = self.request.query_params.get('corbeille', '0') == '1'
        try:
            if user.profil.role == 'CLIENT':
                return BonCommande.objects.none()
        except Exception:
            pass
        return BonCommande.objects.filter(is_deleted=show_deleted)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return BonCommandeCreateSerializer
        return BonCommandeSerializer

    # ✅ Soft delete
    def destroy(self, request, *args, **kwargs):
        bon = self.get_object()
        bon.soft_delete()
        return Response({'success': 'Bon déplacé dans la corbeille.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='restaurer')
    def restaurer(self, request, pk=None):
        try:
            bon = BonCommande.objects.get(pk=pk)
        except BonCommande.DoesNotExist:
            return Response({'error': 'Bon introuvable'}, status=404)
        bon.restore()
        return Response({'success': f'{bon.numero} restauré.'})

    @action(detail=True, methods=['delete'], url_path='supprimer_definitif')
    def supprimer_definitif(self, request, pk=None):
        try:
            bon = BonCommande.objects.get(pk=pk)
        except BonCommande.DoesNotExist:
            return Response({'error': 'Bon introuvable'}, status=404)
        if bon.pdf_file:
            bon.pdf_file.delete(save=False)
        bon.delete()
        return Response({'success': 'Supprimé définitivement.'})

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        try:
            bon = self.get_object()
            if bon.pdf_file:
                bon.pdf_file.delete(save=True)
        except Exception:
            pass
        return response

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def generer_pdf(self, request, pk=None):
        bon = self.get_object()
        try:
            if bon.pdf_file:
                bon.pdf_file.delete(save=False)
            generer_pdf_bon_commande(bon)
            return Response({'success': f'PDF généré : {bon.numero}.pdf'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    @action(detail=True, methods=['get'])
    def pdf(self, request, pk=None):
        bon = self.get_object()
        try:
            if bon.pdf_file:
                bon.pdf_file.delete(save=False)
            generer_pdf_bon_commande(bon)
            bon.refresh_from_db()
        except Exception as e:
            return Response({'error': f'Impossible de générer le PDF : {str(e)}'}, status=500)
        response = FileResponse(bon.pdf_file.open('rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{bon.numero}.pdf"'
        return response


class LigneBonCommandeViewSet(viewsets.ModelViewSet):
    queryset           = LigneBonCommande.objects.all()
    serializer_class   = LigneBonCommandeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend]
    filterset_fields   = ['bon_commande']