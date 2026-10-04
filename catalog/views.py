from rest_framework import viewsets
from .models import (Cliente, Projeto, Equipamento, Atividade, Colaborador,
                     Orcamento, ProjetoEquipamento, ProjetoEquipamentoAtividade)
from .serializers import (
    ClienteSerializer, ProjetoSerializer, EquipamentoSerializer,
    AtividadeSerializer, ColaboradorSerializer, OrcamentoSerializer,
    ProjetoEquipamentoSerializer, ProjetoEquipamentoAtividadeSerializer
)
from core.permissions import IsPlanejadorOrReadOnly

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsPlanejadorOrReadOnly]

from rest_framework.decorators import action
from rest_framework.response import Response

class ProjetoViewSet(viewsets.ModelViewSet):
    queryset = Projeto.objects.select_related('cliente', 'orcamento').all() # Eager loading
    serializer_class = ProjetoSerializer
    permission_classes = [IsPlanejadorOrReadOnly]

    @action(detail=True, methods=['get'])
    def kpis(self, request, pk=None):
        projeto = self.get_object()
        from operations.services import ProjetoAnalyticsService
        dados = ProjetoAnalyticsService.calcular_kpis(projeto)
        if "error" in dados:
            return Response({"error": dados["error"]}, status=400)
        return Response(dados)

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

class OrcamentoViewSet(viewsets.ModelViewSet):
    queryset = Orcamento.objects.select_related('projeto').all()
    serializer_class = OrcamentoSerializer
    permission_classes = [IsPlanejadorOrReadOnly]

class ProjetoEquipamentoViewSet(viewsets.ModelViewSet):
    queryset = ProjetoEquipamento.objects.select_related('projeto', 'equipamento').all()
    serializer_class = ProjetoEquipamentoSerializer
    permission_classes = [IsPlanejadorOrReadOnly]
    filterset_fields = ['projeto', 'equipamento']

class ProjetoEquipamentoAtividadeViewSet(viewsets.ModelViewSet):
    queryset = ProjetoEquipamentoAtividade.objects.select_related('projeto_equipamento', 'atividade').all()
    serializer_class = ProjetoEquipamentoAtividadeSerializer
    permission_classes = [IsPlanejadorOrReadOnly]
    filterset_fields = ['projeto_equipamento', 'atividade']
