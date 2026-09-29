from rest_framework import viewsets
from .models import Apontamento
from .serializers import ApontamentoSerializer
from core.mixins import RLSMixin
from core.permissions import IsPlanejadorOrOwner

class ApontamentoViewSet(RLSMixin, viewsets.ModelViewSet):
    """
    ViewSet para gerenciar apontamentos.
    Utiliza RLSMixin para garantir que técnicos só vejam seus apontamentos.
    Utiliza IsPlanejadorOrOwner para garantir permissões no nível de objeto.
    """
    queryset = Apontamento.objects.select_related(
        'projeto', 'equipamento', 'atividade', 'colaborador'
    ).all()
    serializer_class = ApontamentoSerializer
    permission_classes = [IsPlanejadorOrOwner]
