from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Profil, DemandeApplication
from .serializers import UserSerializer, RegisterSerializer, DemandeApplicationSerializer


class RegisterView(generics.CreateAPIView):
    queryset           = User.objects.all()
    serializer_class   = RegisterSerializer
    permission_classes = [AllowAny]


class DemandeApplicationView(generics.CreateAPIView):
    """Endpoint public — créer une demande d'application."""
    queryset           = DemandeApplication.objects.all()
    serializer_class   = DemandeApplicationSerializer
    permission_classes = [AllowAny]


class DemandeApplicationListView(generics.ListAPIView):
    """Liste des demandes — Admin seulement."""
    queryset           = DemandeApplication.objects.all()
    serializer_class   = DemandeApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            if self.request.user.profil.role != 'ADMIN':
                return DemandeApplication.objects.none()
        except Exception:
            return DemandeApplication.objects.none()
        return DemandeApplication.objects.all()


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_demande_statut(request, pk):
    """Mettre à jour le statut d'une demande."""
    try:
        demande = DemandeApplication.objects.get(pk=pk)
    except DemandeApplication.DoesNotExist:
        return Response({'error': 'Demande introuvable'}, status=status.HTTP_404_NOT_FOUND)

    demande.statut          = request.data.get('statut', demande.statut)
    demande.notes_internes  = request.data.get('notes_internes', demande.notes_internes)
    demande.save()
    return Response(DemandeApplicationSerializer(demande).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mon_profil(request):
    user = request.user
    try:
        role = user.profil.role
    except Exception:
        role = 'EMPLOYE'
    return Response({
        'id':         user.id,
        'username':   user.username,
        'email':      user.email,
        'first_name': user.first_name,
        'last_name':  user.last_name,
        'role':       role,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def liste_utilisateurs(request):
    try:
        if request.user.profil.role != 'ADMIN':
            return Response({'error': 'Accès refusé'}, status=status.HTTP_403_FORBIDDEN)
    except Exception:
        return Response({'error': 'Accès refusé'}, status=status.HTTP_403_FORBIDDEN)
    users = User.objects.all().select_related('profil')
    return Response(UserSerializer(users, many=True).data)