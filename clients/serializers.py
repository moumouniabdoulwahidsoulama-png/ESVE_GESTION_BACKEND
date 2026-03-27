from rest_framework import serializers
from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Client
        fields = '__all__'

    def validate_email(self, value):
        """Email optionnel — accepte chaîne vide."""
        if value == '':
            return value
        # Validation format email si renseigné
        import re
        if value and not re.match(r'^[^@]+@[^@]+\.[^@]+$', value):
            raise serializers.ValidationError("Format d'email invalide.")
        return value

    def validate_telephone(self, value):
        """Téléphone requis — ne doit pas être vide."""
        if not value or value.strip() == '':
            raise serializers.ValidationError("Le téléphone est requis.")
        return value


class ClientListSerializer(serializers.ModelSerializer):
    """Version allégée pour les listes déroulantes."""
    class Meta:
        model  = Client
        fields = ['id', 'nom_entreprise', 'telephone', 'email', 'adresse', 'ifu']