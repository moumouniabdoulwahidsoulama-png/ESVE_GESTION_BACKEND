from rest_framework import serializers
from .models import Facture, LigneFacture
from clients.serializers import ClientListSerializer
import uuid


class LigneFactureSerializer(serializers.ModelSerializer):
    class Meta:
        model  = LigneFacture
        fields = '__all__'
        read_only_fields = ['total_ht', 'facture']
        extra_kwargs = {
            'facture': {'required': False}
        }


class FactureSerializer(serializers.ModelSerializer):
    lignes        = LigneFactureSerializer(many=True, read_only=True)
    client_detail = ClientListSerializer(source='client', read_only=True)

    class Meta:
        model  = Facture
        fields = '__all__'
        read_only_fields = [
            'numero', 'total_ht_brut', 'montant_remise',
            'total_ht', 'tva_18pct', 'retenue_5pct', 'bic_2pct', 'total_net'
        ]


class FactureCreateSerializer(serializers.ModelSerializer):
    lignes = LigneFactureSerializer(many=True, required=False)

    class Meta:
        model  = Facture
        fields = '__all__'
        read_only_fields = [
            'numero', 'total_ht_brut', 'montant_remise',
            'total_ht', 'tva_18pct', 'retenue_5pct', 'bic_2pct', 'total_net'
        ]

    def create(self, validated_data):
        lignes_data = validated_data.pop('lignes', [])

        # Numéro temporaire unique
        validated_data['numero'] = f"TEMP-{uuid.uuid4().hex[:8].upper()}"

        facture = Facture.objects.create(**validated_data)

        # Générer le vrai numéro
        facture.generer_numero()

        # Créer les lignes
        for ligne_data in lignes_data:
            LigneFacture.objects.create(facture=facture, **ligne_data)

        # Recalculer les totaux avec les bons flags
        facture.refresh_from_db()
        facture.calculer_totaux()

        return facture

    def update(self, instance, validated_data):
        lignes_data = validated_data.pop('lignes', None)

        # Mettre à jour tous les champs y compris les flags
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if lignes_data is not None:
            instance.lignes.all().delete()
            for ligne_data in lignes_data:
                LigneFacture.objects.create(facture=instance, **ligne_data)

        # Recalculer avec les nouveaux flags
        instance.refresh_from_db()
        instance.calculer_totaux()

        return instance