from rest_framework import serializers
from .models import BonCommande, LigneBonCommande


class LigneBonCommandeSerializer(serializers.ModelSerializer):
    class Meta:
        model  = LigneBonCommande
        fields = '__all__'
        read_only_fields = ['total_ht', 'bon_commande']
        extra_kwargs = {
            'bon_commande': {'required': False}
        }


class BonCommandeSerializer(serializers.ModelSerializer):
    lignes = LigneBonCommandeSerializer(many=True, read_only=True)

    class Meta:
        model  = BonCommande
        fields = '__all__'
        read_only_fields = ['numero', 'total_ht', 'retenue_5pct', 'bic_2pct', 'total_net']


class BonCommandeCreateSerializer(serializers.ModelSerializer):
    lignes = LigneBonCommandeSerializer(many=True, required=False)

    class Meta:
        model  = BonCommande
        fields = '__all__'
        read_only_fields = ['numero', 'total_ht', 'retenue_5pct', 'bic_2pct', 'total_net']

    def create(self, validated_data):
        lignes_data = validated_data.pop('lignes', [])
        bon         = BonCommande.objects.create(**validated_data)

        # Générer le numéro auto
        bon.generer_numero()

        # Créer les lignes
        for ligne_data in lignes_data:
            LigneBonCommande.objects.create(bon_commande=bon, **ligne_data)

        if lignes_data:
            bon.calculer_totaux()

        return bon

    def update(self, instance, validated_data):
        lignes_data = validated_data.pop('lignes', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if lignes_data is not None:
            instance.lignes.all().delete()
            for ligne_data in lignes_data:
                LigneBonCommande.objects.create(bon_commande=instance, **ligne_data)
            instance.calculer_totaux()

        return instance