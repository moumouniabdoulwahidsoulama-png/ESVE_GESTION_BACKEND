from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from .pdf_generator import generer_pdf_offre


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generer_offre_service(request):
    """
    Génère un PDF d'offre de service.
    Body JSON :
    {
        "langue": "fr" | "en",
        "societe": "Nom de la société destinataire",
        "destinataires": [
            {"nom": "Jean Dupont", "fonction": "Directeur Achats"},
            {"nom": "Marie Martin", "fonction": "Responsable Technique"},
            {"nom": "", "fonction": ""}
        ],
        "texte_custom": "Paragraphe additionnel optionnel..."
    }
    """
    data = request.data

    # Validation basique
    langue = data.get('langue', 'fr')
    if langue not in ('fr', 'en'):
        return Response({'error': 'langue doit être "fr" ou "en"'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        pdf_bytes = generer_pdf_offre(data)
    except Exception as e:
        return Response({'error': str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    societe   = data.get('societe', 'offre').replace(' ', '_')[:30]
    lang_sfx  = 'FR' if langue == 'fr' else 'EN'
    filename  = f"ESVE_Offre_Service_{lang_sfx}_{societe}.pdf"

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response