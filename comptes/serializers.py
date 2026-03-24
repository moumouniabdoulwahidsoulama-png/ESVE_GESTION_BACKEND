from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profil, DemandeApplication


class ProfilSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Profil
        fields = ['role', 'telephone']


class UserSerializer(serializers.ModelSerializer):
    profil = ProfilSerializer(read_only=True)

    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profil']


class RegisterSerializer(serializers.ModelSerializer):
    role      = serializers.ChoiceField(choices=['ADMIN', 'EMPLOYE', 'CLIENT'], default='EMPLOYE')
    telephone = serializers.CharField(required=False, allow_blank=True)
    password  = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model  = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'role', 'telephone']

    def create(self, validated_data):
        role      = validated_data.pop('role', 'EMPLOYE')
        telephone = validated_data.pop('telephone', '')
        password  = validated_data.pop('password')
        user      = User.objects.create_user(**validated_data, password=password)
        Profil.objects.create(user=user, role=role, telephone=telephone)
        return user


class DemandeApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = DemandeApplication
        fields = '__all__'
        read_only_fields = ['statut', 'notes_internes', 'date_demande', 'date_modification']