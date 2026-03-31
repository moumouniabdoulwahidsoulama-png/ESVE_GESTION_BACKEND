from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse
from .models import OffreService
from .serializers import OffreServiceSerializer
from .pdf_generator import generer_pdf_offre


class OffreServiceViewSet(viewsets.ModelViewSet):
    queryset           = OffreService.objects.all().order_by('-date_creation')
    serializer_class   = OffreServiceSerializer
    permission_classes = [IsAuthenticated]

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


# ✅ Vue séparée pour la génération directe sans sauvegarde
# URL: /api/v1/offres/generer-pdf/  (évite le conflit avec le router DRF)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generer_offre_pdf(request):
    """
    Génère un PDF d'offre de service sans sauvegarder en base.
    POST /api/v1/offres/generer-pdf/
    """
    data   = request.data
    langue = data.get('langue', 'fr')
    if langue not in ('fr', 'en'):
        return Response({'error': 'langue doit être "fr" ou "en"'}, status=400)
    try:
        pdf_bytes = generer_pdf_offre(data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    soc      = (data.get('societe') or 'offre').replace(' ', '_')[:30]
    filename = f"ESVE_Offre_{langue.upper()}_{soc}.pdf"
    resp = HttpResponse(pdf_bytes, content_type='application/pdf')
    resp['Content-Disposition'] = f'attachment; filename="{filename}"'
    return resp