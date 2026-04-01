from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse
from .models import OffreService
from .serializers import OffreServiceSerializer
from .pdf_generator import generer_pdf_offre


class OffreServiceViewSet(viewsets.ModelViewSet):
    serializer_class   = OffreServiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        show_deleted = self.request.query_params.get('corbeille', '0') == '1'
        return OffreService.objects.filter(is_deleted=show_deleted)

    # Soft delete au lieu de vraiment supprimer
    def destroy(self, request, *args, **kwargs):
        offre = self.get_object()
        offre.soft_delete()
        return Response({'success': 'Offre déplacée dans la corbeille.'})

    @action(detail=True, methods=['post'], url_path='restaurer')
    def restaurer(self, request, pk=None):
        try:
            offre = OffreService.objects.get(pk=pk)
        except OffreService.DoesNotExist:
            return Response({'error': 'Offre introuvable'}, status=404)
        offre.restore()
        return Response({'success': 'Offre restaurée.'})

    @action(detail=True, methods=['delete'], url_path='supprimer_definitif')
    def supprimer_definitif(self, request, pk=None):
        try:
            offre = OffreService.objects.get(pk=pk)
        except OffreService.DoesNotExist:
            return Response({'error': 'Offre introuvable'}, status=404)
        offre.delete()
        return Response({'success': 'Offre supprimée définitivement.'})

    @action(detail=True, methods=['get'])
    def pdf(self, request, pk=None):
        offre = self.get_object()
        data  = {
            'langue':        offre.langue,
            'societe':       offre.societe,
            'destinataires': offre.destinataires,
            'texte_custom':  offre.texte_custom,
        }
        try:
            pdf_bytes = generer_pdf_offre(data)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
        soc      = offre.societe.replace(' ', '_')[:30] if offre.societe else 'offre'
        filename = f"ESVE_Offre_{offre.langue.upper()}_{soc}.pdf"
        resp = HttpResponse(pdf_bytes, content_type='application/pdf')
        resp['Content-Disposition'] = f'attachment; filename="{filename}"'
        return resp


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generer_offre_service(request):
    data   = request.data
    langue = data.get('langue', 'fr')
    if langue not in ('fr', 'en'):
        return Response({'error': 'langue doit etre "fr" ou "en"'}, status=400)
    try:
        pdf_bytes = generer_pdf_offre(data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    soc      = (data.get('societe') or 'offre').replace(' ', '_')[:30]
    filename = f"ESVE_Offre_{langue.upper()}_{soc}.pdf"
    resp = HttpResponse(pdf_bytes, content_type='application/pdf')
    resp['Content-Disposition'] = f'attachment; filename="{filename}"'
    return resp