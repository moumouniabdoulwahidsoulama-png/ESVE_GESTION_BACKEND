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

        # ✅ Désactiver les signaux pendant la création pour éviter la double création
        facture = Facture.objects.create(**validated_data)

        # Générer le vrai numéro
        facture.generer_numero()

        # ✅ Créer les lignes sans déclencher calculer_totaux à chaque fois
        lignes_a_creer = []
        for ligne_data in lignes_data:
            ligne = LigneFacture(facture=facture, **ligne_data)
            ligne.total_ht = round(ligne.prix_unitaire_ht * ligne.quantite, 2)
            lignes_a_creer.append(ligne)

        # bulk_create évite les appels à save() individuels (pas de signal calculer_totaux)
        if lignes_a_creer:
            LigneFacture.objects.bulk_create(lignes_a_creer)

        # Recalculer une seule fois à la fin
        facture.refresh_from_db()
        facture.calculer_totaux()

        return facture

    def update(self, instance, validated_data):
        lignes_data = validated_data.pop('lignes', None)

        # Mettre à jour tous les champs
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if lignes_data is not None:
            # ✅ Supprimer les anciennes lignes sans déclencher calculer_totaux
            instance.lignes.all().delete()

            # ✅ Recréer les lignes avec bulk_create
            lignes_a_creer = []
            for ligne_data in lignes_data:
                ligne = LigneFacture(facture=instance, **ligne_data)
                ligne.total_ht = round(ligne.prix_unitaire_ht * ligne.quantite, 2)
                lignes_a_creer.append(ligne)

            if lignes_a_creer:
                LigneFacture.objects.bulk_create(lignes_a_creer)

        # Recalculer une seule fois
        instance.refresh_from_db()
        instance.calculer_totaux()

        return instance