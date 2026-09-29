from rest_framework import viewsets
from .models import Cliente, Projeto, Equipamento, Atividade, Colaborador
from .serializers import (
    ClienteSerializer, ProjetoSerializer, EquipamentoSerializer,
    AtividadeSerializer, ColaboradorSerializer
)
from core.permissions import IsPlanejadorOrReadOnly

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsPlanejadorOrReadOnly]

class ProjetoViewSet(viewsets.ModelViewSet):
    queryset = Projeto.objects.select_related('cliente').all() # Eager loading
    serializer_class = ProjetoSerializer
    permission_classes = [IsPlanejadorOrReadOnly]

class EquipamentoViewSet(viewsets.ModelViewSet):
    queryset = Equipamento.objects.all()
    serializer_class = EquipamentoSerializer
    permission_classes = [IsPlanejadorOrReadOnly]

class AtividadeViewSet(viewsets.ModelViewSet):
    queryset = Atividade.objects.all()
    serializer_class = AtividadeSerializer
    permission_classes = [IsPlanejadorOrReadOnly]

class ColaboradorViewSet(viewsets.ModelViewSet):
    queryset = Colaborador.objects.select_related('usuario').all()
    serializer_class = ColaboradorSerializer
    permission_classes = [IsPlanejadorOrReadOnly]
