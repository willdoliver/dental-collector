from rest_framework import serializers
from .models import Dentista

class DentistaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dentista
        # fields = '__all__'
        fields = ('nome', 'cfo', 'uf')