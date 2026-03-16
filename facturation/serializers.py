from rest_framework import serializers
from .models import Facture, LigneFacture
from clients.serializers import ClientListSerializer


class LigneFactureSerializer(serializers.ModelSerializer):
    class Meta:
        model  = LigneFacture
        fields = '__all__'
        read_only_fields = ['total_ht', 'facture']  # ← on ajoute 'facture' ici
        extra_kwargs = {
            'facture': {'required': False}  # ← pas obligatoire à la création
        }


class FactureSerializer(serializers.ModelSerializer):
    lignes         = LigneFactureSerializer(many=True, read_only=True)
    client_detail  = ClientListSerializer(source='client', read_only=True)

    class Meta:
        model  = Facture
        fields = '__all__'
        read_only_fields = ['numero', 'total_ht', 'retenue_5pct', 'bic_2pct', 'total_net']


class FactureCreateSerializer(serializers.ModelSerializer):
    """Utilisé uniquement pour la création/modification."""
    lignes = LigneFactureSerializer(many=True, required=False)

    class Meta:
        model  = Facture
        fields = '__all__'
        read_only_fields = ['numero', 'total_ht', 'retenue_5pct', 'bic_2pct', 'total_net']

    def create(self, validated_data):
        lignes_data = validated_data.pop('lignes', [])
        facture     = Facture.objects.create(**validated_data)

        # Générer le numéro auto
        facture.generer_numero()

        # Créer les lignes
        for ligne_data in lignes_data:
            LigneFacture.objects.create(facture=facture, **ligne_data)

        # Recalculer les totaux
        if lignes_data:
            facture.calculer_totaux()

        return facture

    def update(self, instance, validated_data):
        lignes_data = validated_data.pop('lignes', None)

        # Mettre à jour les champs de la facture
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Si des lignes sont fournies, remplacer les anciennes
        if lignes_data is not None:
            instance.lignes.all().delete()
            for ligne_data in lignes_data:
                LigneFacture.objects.create(facture=instance, **ligne_data)
            instance.calculer_totaux()

        return instance