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
        try:
            if user.profil.role == 'CLIENT':
                return BonCommande.objects.none()
        except Exception:
            pass
        # ✅ Par défaut : n'afficher que les non supprimés
        return BonCommande.objects.filter(is_deleted=False)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return BonCommandeCreateSerializer
        return BonCommandeSerializer

    # ✅ Override destroy — soft delete au lieu de vraie suppression
    def destroy(self, request, *args, **kwargs):
        bon = self.get_object()
        bon.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ✅ Corbeille — liste des bons supprimés
    @action(detail=False, methods=['get'])
    def corbeille(self, request):
        bons = BonCommande.objects.filter(is_deleted=True)
        serializer = BonCommandeSerializer(bons, many=True)
        return Response(serializer.data)

    # ✅ Restaurer un bon depuis la corbeille
    @action(detail=True, methods=['post'])
    def restaurer(self, request, pk=None):
        try:
            bon = BonCommande.objects.get(pk=pk)
        except BonCommande.DoesNotExist:
            return Response({'error': 'Document introuvable.'}, status=status.HTTP_404_NOT_FOUND)
        if not bon.is_deleted:
            return Response({'error': 'Ce document n\'est pas dans la corbeille.'}, status=status.HTTP_400_BAD_REQUEST)
        bon.restaurer()
        return Response(BonCommandeSerializer(bon).data)

    # ✅ Suppression définitive depuis la corbeille
    @action(detail=True, methods=['delete'])
    def supprimer_definitif(self, request, pk=None):
        try:
            bon = BonCommande.objects.get(pk=pk)
        except BonCommande.DoesNotExist:
            return Response({'error': 'Document introuvable.'}, status=status.HTTP_404_NOT_FOUND)
        bon.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def generer_pdf(self, request, pk=None):
        bon = self.get_object()
        try:
            if bon.pdf_file:
                bon.pdf_file.delete(save=False)
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
        bon = self.get_object()
        try:
            if bon.pdf_file:
                bon.pdf_file.delete(save=False)
            generer_pdf_bon_commande(bon)
            bon.refresh_from_db()
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