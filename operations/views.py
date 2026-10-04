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

    from rest_framework.decorators import action
    from rest_framework.response import Response

    @action(detail=True, methods=['post'])
    def aprovar(self, request, pk=None):
        from catalog.models import ProjetoEquipamentoAtividade
        from operations.services import EquipamentoProdutividadeService

        apontamento = self.get_object()
        if apontamento.status == 'APROVADO':
            return Response({"error": "Apontamento já aprovado"}, status=400)
        
        apontamento.status = 'APROVADO'
        apontamento.save()

        # Gatilho do Autoajuste
        try:
            pea = ProjetoEquipamentoAtividade.objects.get(
                projeto_equipamento__projeto=apontamento.projeto,
                projeto_equipamento__equipamento=apontamento.equipamento,
                atividade=apontamento.atividade
            )
            EquipamentoProdutividadeService.recalcular_tempo_medio(pea)
        except ProjetoEquipamentoAtividade.DoesNotExist:
            pass # Ignora se não houver setup configurado para essa combinação

        return Response({"status": "Aprovado"})

    @action(detail=True, methods=['post'])
    def rejeitar(self, request, pk=None):
        apontamento = self.get_object()
        apontamento.status = 'REJEITADO'
        apontamento.save()
        return Response({"status": "Rejeitado"})
