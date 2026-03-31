from rest_framework import serializers

from .models import OffreService


class OffreServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model  = OffreService
        fields = '__all__'