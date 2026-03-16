from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Client
from .serializers import ClientSerializer, ClientListSerializer


class ClientViewSet(viewsets.ModelViewSet):
    queryset           = Client.objects.filter(actif=True)
    serializer_class   = ClientSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['actif', 'regime_imposition']
    search_fields      = ['nom_entreprise', 'contact_nom', 'email', 'ifu', 'rccm']
    ordering_fields    = ['nom_entreprise', 'date_creation']

    def get_serializer_class(self):
        if self.action == 'list':
            return ClientListSerializer
        return ClientSerializer