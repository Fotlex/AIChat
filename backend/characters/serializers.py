from rest_framework import serializers
from .models import Character

class CharacterListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Character
        
        fields = [
            'id',
            'name',
            'description',
            'photo',
        ]