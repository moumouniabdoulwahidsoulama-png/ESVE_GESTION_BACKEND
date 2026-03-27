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

    demande.statut         = request.data.get('statut', demande.statut)
    demande.notes_internes = request.data.get('notes_internes', demande.notes_internes)
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
    """Liste tous les utilisateurs — Admin seulement."""
    try:
        if request.user.profil.role != 'ADMIN':
            return Response({'error': 'Accès refusé'}, status=status.HTTP_403_FORBIDDEN)
    except Exception:
        return Response({'error': 'Accès refusé'}, status=status.HTTP_403_FORBIDDEN)
    users = User.objects.all().select_related('profil')
    return Response(UserSerializer(users, many=True).data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def supprimer_utilisateur(request, pk):
    """Supprimer un utilisateur — Admin seulement."""
    try:
        if request.user.profil.role != 'ADMIN':
            return Response({'error': 'Accès refusé'}, status=status.HTTP_403_FORBIDDEN)
    except Exception:
        return Response({'error': 'Accès refusé'}, status=status.HTTP_403_FORBIDDEN)

    # Empêcher l'admin de se supprimer lui-même
    if request.user.id == pk:
        return Response(
            {'error': 'Vous ne pouvez pas supprimer votre propre compte.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({'error': 'Utilisateur introuvable'}, status=status.HTTP_404_NOT_FOUND)

    username = user.username
    user.delete()
    return Response(
        {'success': f'Utilisateur {username} supprimé.'},
        status=status.HTTP_200_OK
    )


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def modifier_utilisateur(request, pk):
    """Modifier un utilisateur (role, nom) — Admin seulement."""
    try:
        if request.user.profil.role != 'ADMIN':
            return Response({'error': 'Accès refusé'}, status=status.HTTP_403_FORBIDDEN)
    except Exception:
        return Response({'error': 'Accès refusé'}, status=status.HTTP_403_FORBIDDEN)

    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({'error': 'Utilisateur introuvable'}, status=status.HTTP_404_NOT_FOUND)

    # Mettre à jour les champs de base
    if 'first_name' in request.data:
        user.first_name = request.data['first_name']
    if 'last_name' in request.data:
        user.last_name = request.data['last_name']
    if 'email' in request.data:
        user.email = request.data['email']
    if 'is_active' in request.data:
        user.is_active = request.data['is_active']
    user.save()

    # Mettre à jour le rôle
    if 'role' in request.data:
        try:
            user.profil.role = request.data['role']
            user.profil.save()
        except Exception:
            pass

    return Response(UserSerializer(user).data)