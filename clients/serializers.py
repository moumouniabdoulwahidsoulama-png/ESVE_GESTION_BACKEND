from rest_framework import serializers
from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Client
        fields = '__all__'


class ClientListSerializer(serializers.ModelSerializer):
    """Version allégée pour les listes déroulantes."""
    class Meta:
        model  = Client
        fields = ['id', 'nom_entreprise', 'telephone', 'email']