from rest_framework import generics
from .models import Dentista
from .serializers import DentistaSerializer

class DentistaList(generics.ListCreateAPIView):
    queryset = Dentista.objects.all()
    serializer_class = DentistaSerializer