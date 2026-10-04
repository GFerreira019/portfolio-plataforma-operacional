from django.db.models import Sum, F
from decimal import Decimal
from datetime import timedelta
import datetime

class ProjetoAnalyticsService:
    @staticmethod
    def calcular_kpis(projeto):
        """
        Calcula os KPIs (Key Performance Indicators) determinísticos de um projeto.
        Retorna um dicionário com todos os indicadores matemáticos, lidando com 
        divisões por zero e ausência de dados.
        """
        # Obter o Orçamento (Previsto)
        orcamento = getattr(projeto, 'orcamento', None)
        if not orcamento:
            return {"error": "Projeto não possui orçamento vinculado."}
        
        # Obter os Apontamentos APROVADOS (Realizado)
        # O custo_realizado do BD é a soma de (horas * custo_hora snapshot)
        agregados = projeto.apontamento_set.filter(status='APROVADO').aggregate(
            total_horas=Sum('horas'),
            total_quantidade=Sum('quantidade'),
            total_custo=Sum(F('horas') * F('custo_hora'))
        )

        # Tratar nulos caso não haja apontamentos
        horas_realizadas = agregados['total_horas'] or Decimal('0.00')
        quantidade_realizada = agregados['total_quantidade'] or Decimal('0.00')
        custo_realizado = agregados['total_custo'] or Decimal('0.00')

        # Dados Previstos
        horas_previstas = Decimal(str(orcamento.horas_previstas))
        quantidade_prevista = Decimal(str(orcamento.quantidade_prevista))
        custo_previsto = Decimal(str(orcamento.custo_previsto))

        # 1. Avanço Físico (%)
        avanco_fisico_pct = Decimal('0.00')
        if quantidade_prevista > 0:
            avanco_fisico_pct = (quantidade_realizada / quantidade_prevista) * 100

        # 2. Desvio de Custo
        desvio_custo_abs = custo_realizado - custo_previsto
        desvio_custo_pct = Decimal('0.00')
        if custo_previsto > 0:
            desvio_custo_pct = (desvio_custo_abs / custo_previsto) * 100

        # 3. Ritmo de Execução (Unidades por Hora)
        ritmo_execucao = Decimal('0.00')
        if horas_realizadas > 0:
            ritmo_execucao = quantidade_realizada / horas_realizadas

        # 4. Previsão de Horas Finais e Desvio de Prazo
        # Se o ritmo for > 0, extrapolamos. Senão, mantemos as horas previstas.
        previsao_horas_finais = horas_previstas
        if ritmo_execucao > 0:
            previsao_horas_finais = quantidade_prevista / ritmo_execucao

        desvio_horas = previsao_horas_finais - horas_previstas

        return {
            "previsto": {
                "horas": horas_previstas,
                "quantidade": quantidade_prevista,
                "custo": custo_previsto,
                "prazo": orcamento.prazo_previsto
            },
            "realizado": {
                "horas": horas_realizadas,
                "quantidade": quantidade_realizada,
                "custo": custo_realizado
            },
            "kpis": {
                "avanco_fisico_pct": round(avanco_fisico_pct, 2),
                "desvio_custo_abs": round(desvio_custo_abs, 2),
                "desvio_custo_pct": round(desvio_custo_pct, 2),
                "ritmo_execucao_unid_por_hora": round(ritmo_execucao, 4),
                "previsao_horas_finais": round(previsao_horas_finais, 2),
                "desvio_horas_abs": round(desvio_horas, 2)
            }
        }

class EquipamentoProdutividadeService:
    @staticmethod
    def recalcular_tempo_medio(projeto_equipamento_atividade):
        from operations.models import Apontamento
        from decimal import Decimal

        apontamentos = Apontamento.objects.filter(
            projeto=projeto_equipamento_atividade.projeto_equipamento.projeto,
            equipamento=projeto_equipamento_atividade.projeto_equipamento.equipamento,
            atividade=projeto_equipamento_atividade.atividade,
            status='APROVADO'
        )

        total_horas = sum(a.horas for a in apontamentos)
        total_quantidade = sum(a.quantidade for a in apontamentos)
        total_amostras = apontamentos.count()

        projeto_equipamento_atividade.total_amostras = total_amostras

        if total_quantidade > Decimal('0.00'):
            tempo_medio_real = total_horas / total_quantidade
            projeto_equipamento_atividade.tempo_medio_real = tempo_medio_real

            if projeto_equipamento_atividade.tempo_medio_estimado > Decimal('0.00'):
                desvio = ((tempo_medio_real - projeto_equipamento_atividade.tempo_medio_estimado) / projeto_equipamento_atividade.tempo_medio_estimado) * 100
                projeto_equipamento_atividade.desvio_tempo_pct = desvio
            else:
                projeto_equipamento_atividade.desvio_tempo_pct = None
        else:
            projeto_equipamento_atividade.tempo_medio_real = None
            projeto_equipamento_atividade.desvio_tempo_pct = None
        
        projeto_equipamento_atividade.save()
