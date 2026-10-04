from django.test import TestCase
from django.contrib.auth.models import User, Group
from rest_framework.test import APIClient
from catalog.models import Cliente, Projeto, Equipamento, ProjetoEquipamento, Atividade, ProjetoEquipamentoAtividade, Colaborador
from operations.models import Apontamento
from datetime import date, timedelta
from decimal import Decimal

class RLSAndPermissionsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Criar os grupos (caso não existam)
        self.grupo_tecnico, _ = Group.objects.get_or_create(name='Técnico de Campo')
        self.grupo_planejador, _ = Group.objects.get_or_create(name='Planejador/Analista')
        
        # Criar os usuários
        self.user_tecnico1 = User.objects.create_user(username='tecnico1', password='pwd')
        self.user_tecnico1.groups.add(self.grupo_tecnico)
        self.colab1 = Colaborador.objects.create(nome='Técnico Um', usuario=self.user_tecnico1, custo_hora=50.0)

        self.user_tecnico2 = User.objects.create_user(username='tecnico2', password='pwd')
        self.user_tecnico2.groups.add(self.grupo_tecnico)
        self.colab2 = Colaborador.objects.create(nome='Técnico Dois', usuario=self.user_tecnico2, custo_hora=60.0)

        self.user_planejador = User.objects.create_user(username='planejador', password='pwd')
        self.user_planejador.groups.add(self.grupo_planejador)
        self.colab_plan = Colaborador.objects.create(nome='Planejador', usuario=self.user_planejador, custo_hora=100.0)

        # Configurar catálogo base para apontamentos
        self.cliente = Cliente.objects.create(codigo='CLI1', nome='Cliente 1')
        self.projeto = Projeto.objects.create(cliente=self.cliente, codigo='PRJ1')
        self.equip = Equipamento.objects.create(codigo='EQ1', nome='Equip 1')
        self.pe = ProjetoEquipamento.objects.create(projeto=self.projeto, equipamento=self.equip)
        self.ativ = Atividade.objects.create(codigo='AT1', nome='Ativ 1')
        self.pea = ProjetoEquipamentoAtividade.objects.create(projeto_equipamento=self.pe, atividade=self.ativ)

        # Criar Apontamentos Iniciais
        self.apont_t1 = Apontamento.objects.create(
            projeto=self.projeto,
            equipamento=self.equip,
            atividade=self.ativ,
            colaborador=self.colab1,
            data=date.today(),
            horas=4.0
        )

        self.apont_t2 = Apontamento.objects.create(
            projeto=self.projeto,
            equipamento=self.equip,
            atividade=self.ativ,
            colaborador=self.colab2,
            data=date.today(),
            horas=8.0
        )

    def test_idor_tecnico_cannot_edit_others_apontamento(self):
        # Utiliza Permissions ou Mixins indiretamente através de Views, 
        # mas podemos simular invocando a permission class.
        from core.permissions import IsPlanejadorOrOwner
        
        # Simula request
        class MockRequest:
            def __init__(self, user):
                self.user = user

        perm = IsPlanejadorOrOwner()
        
        # Tecnico 1 tentando acessar apontamento do Tecnico 2
        req_t1 = MockRequest(self.user_tecnico1)
        self.assertFalse(perm.has_object_permission(req_t1, None, self.apont_t2))
        
        # Tecnico 1 acessando o próprio apontamento
        self.assertTrue(perm.has_object_permission(req_t1, None, self.apont_t1))

    def test_planejador_can_edit_any_apontamento(self):
        from core.permissions import IsPlanejadorOrOwner
        class MockRequest:
            def __init__(self, user):
                self.user = user
                
        req_plan = MockRequest(self.user_planejador)
        perm = IsPlanejadorOrOwner()
        
        self.assertTrue(perm.has_object_permission(req_plan, None, self.apont_t1))
        self.assertTrue(perm.has_object_permission(req_plan, None, self.apont_t2))

    def test_anti_autoaprovacao(self):
        from operations.serializers import ApontamentoSerializer
        
        class MockRequest:
            def __init__(self, user):
                self.user = user

        # Planejador cria um apontamento pra si mesmo (ele pode agir como técnico)
        apont_plan = Apontamento.objects.create(
            projeto=self.projeto,
            equipamento=self.equip,
            atividade=self.ativ,
            colaborador=self.colab_plan,
            data=date.today(),
            horas=2.0,
            status='EM_ANÁLISE'
        )

        # Ele mesmo tenta aprovar
        serializer = ApontamentoSerializer(instance=apont_plan, data={'status': 'APROVADO'}, partial=True, context={'request': MockRequest(self.user_planejador)})
        self.assertFalse(serializer.is_valid())
        self.assertIn("status", serializer.errors)
        
        # Mas um planejador pode aprovar o do tecnico 1
        serializer_t1 = ApontamentoSerializer(instance=self.apont_t1, data={'status': 'APROVADO'}, partial=True, context={'request': MockRequest(self.user_planejador)})
        self.assertTrue(serializer_t1.is_valid())

    def test_combinacao_invalida_rejeitada(self):
        from operations.serializers import ApontamentoSerializer
        
        class MockRequest:
            def __init__(self, user):
                self.user = user

        # Equipamento 2 (não vinculado ao projeto 1 no PEA)
        equip2 = Equipamento.objects.create(codigo='EQ2', nome='Equip 2')
        
        data = {
            'projeto': self.projeto.id,
            'equipamento': equip2.id,
            'atividade': self.ativ.id,
            'data': '2026-10-01',
            'horas': 5.0
        }
        
        serializer = ApontamentoSerializer(data=data, context={'request': MockRequest(self.user_tecnico1)})
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
        self.assertEqual(str(serializer.errors['non_field_errors'][0]), "A combinação de Projeto, Equipamento e Atividade não possui vínculo pré-cadastrado no catálogo.")
        
        # Testar a combinação Válida
        data_valida = {
            'projeto': self.projeto.id,
            'equipamento': self.equip.id,
            'atividade': self.ativ.id,
            'data': '2026-10-01',
            'horas': 5.0
        }
        
        serializer_valido = ApontamentoSerializer(data=data_valida, context={'request': MockRequest(self.user_tecnico1)})
        self.assertTrue(serializer_valido.is_valid())

    def test_snapshot_historico_imutabilidade(self):
        # O Apontamento inicial (apont_t1) foi criado quando tecnico1 tinha custo_hora=50.0
        self.assertEqual(self.apont_t1.custo_hora, 50.0)
        self.assertEqual(self.apont_t1.custo_realizado, 4.0 * 50.0)
        
        # Simulando uma promoção/aumento
        self.colab1.custo_hora = 75.0
        self.colab1.save()
        
        # O apontamento já existente NÃO DEVE ter seu custo alterado
        self.apont_t1.refresh_from_db()
        self.assertEqual(self.apont_t1.custo_hora, 50.0)
        self.assertEqual(self.apont_t1.custo_realizado, 200.0)
        
        # Um NOVO apontamento deve pegar o novo custo
        novo_apont = Apontamento.objects.create(
            projeto=self.projeto,
            equipamento=self.equip,
            atividade=self.ativ,
            colaborador=self.colab1,
            data=date.today(),
            horas=2.0
        )
        self.assertEqual(novo_apont.custo_hora, 75.0)
        self.assertEqual(novo_apont.custo_realizado, 150.0)

    def test_bloquear_edicao_apontamento_aprovado(self):
        from operations.serializers import ApontamentoSerializer
        from django.core.exceptions import ValidationError

        class MockRequest:
            def __init__(self, user):
                self.user = user

        # O Planejador aprova o apontamento do tecnico 1
        self.apont_t1.status = 'APROVADO'
        self.apont_t1.save()
        
        # 1. Testando via Serializer (API)
        data = {'horas': 10.0} # Tentando mudar as horas
        serializer = ApontamentoSerializer(
            instance=self.apont_t1, 
            data=data, 
            partial=True, 
            context={'request': MockRequest(self.user_planejador)}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
        self.assertEqual(
            str(serializer.errors['non_field_errors'][0]), 
            "Não é permitido editar informações de um apontamento já APROVADO."
        )
        
        # 2. Testando via Model (save)
        with self.assertRaises(ValidationError) as context:
            self.apont_t1.horas = 12.0
            self.apont_t1.save()
        
        self.assertTrue("Não é permitido editar informações de um apontamento já APROVADO." in str(context.exception))

class AnalyticsServiceTestCase(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(codigo='CLI_ANALYTICS', nome='Cliente Analytics')
        self.projeto = Projeto.objects.create(cliente=self.cliente, codigo='PRJ_ANALYTICS')
        self.equip = Equipamento.objects.create(codigo='EQ_AN', nome='Equip')
        self.ativ = Atividade.objects.create(codigo='AT_AN', nome='Ativ')
        
        self.user = User.objects.create_user(username='an_user', password='pwd')
        self.colab = Colaborador.objects.create(nome='Analista', usuario=self.user, custo_hora=100.0)
        
        from catalog.models import Orcamento
        # Orçamento com dados definidos
        self.orcamento = Orcamento.objects.create(
            projeto=self.projeto,
            horas_previstas=100.0,
            quantidade_prevista=500.0,
            custo_previsto=10000.0,
            prazo_previsto=date.today() + timedelta(days=30)
        )

    def test_analise_sem_apontamentos(self):
        from operations.services import ProjetoAnalyticsService
        # Caso: Sem apontamentos, verifica a divisão por zero.
        resultado = ProjetoAnalyticsService.calcular_kpis(self.projeto)
        
        self.assertEqual(resultado['realizado']['horas'], Decimal('0.00'))
        self.assertEqual(resultado['kpis']['avanco_fisico_pct'], Decimal('0.00'))
        self.assertEqual(resultado['kpis']['ritmo_execucao_unid_por_hora'], Decimal('0.00'))
        self.assertEqual(resultado['kpis']['desvio_custo_abs'], Decimal('-10000.00'))

    def test_analise_caso_normal(self):
        from operations.services import ProjetoAnalyticsService
        # Lança 50 horas, faz 250 quantidades -> Metade do projeto.
        # Custo_hora = 100 -> Custo = 50 * 100 = 5000.
        Apontamento.objects.create(
            projeto=self.projeto, equipamento=self.equip, atividade=self.ativ,
            colaborador=self.colab, data=date.today(), horas=50.0, quantidade=250.0, status='APROVADO'
        )
        
        res = ProjetoAnalyticsService.calcular_kpis(self.projeto)
        self.assertEqual(res['realizado']['custo'], Decimal('5000.00'))
        self.assertEqual(res['kpis']['avanco_fisico_pct'], Decimal('50.00')) # 50%
        self.assertEqual(res['kpis']['ritmo_execucao_unid_por_hora'], Decimal('5.00')) # 250 / 50
        self.assertEqual(res['kpis']['previsao_horas_finais'], Decimal('100.00')) # Ritmo exato
        self.assertEqual(res['kpis']['desvio_horas_abs'], Decimal('0.00'))

    def test_analise_atraso_excesso_custo(self):
        from operations.services import ProjetoAnalyticsService
        # Lança 100 horas, mas fez apenas 100 quantidades. Ritmo ruim.
        # Custo_hora = 150 (aumento do analista)
        self.colab.custo_hora = 150.0
        self.colab.save()
        
        Apontamento.objects.create(
            projeto=self.projeto, equipamento=self.equip, atividade=self.ativ,
            colaborador=self.colab, data=date.today(), horas=100.0, quantidade=100.0, status='APROVADO'
        )
        
        res = ProjetoAnalyticsService.calcular_kpis(self.projeto)
        
        # Custo real = 100h * 150 = 15000 (Previsto era 10000)
        self.assertEqual(res['realizado']['custo'], Decimal('15000.00'))
        self.assertEqual(res['kpis']['desvio_custo_abs'], Decimal('5000.00')) # 5000 acima do budget
        self.assertEqual(res['kpis']['desvio_custo_pct'], Decimal('50.00')) # 50% mais caro
        
        # Avanço Físico = 100 / 500 = 20%
        self.assertEqual(res['kpis']['avanco_fisico_pct'], Decimal('20.00'))
        
        # Ritmo = 100 und / 100 h = 1 und/hora
        self.assertEqual(res['kpis']['ritmo_execucao_unid_por_hora'], Decimal('1.00'))
        
        # Previsão: Faltam 400 quantidades. Ritmo de 1 und/h -> Precisa de 500 horas totais.
        self.assertEqual(res['kpis']['previsao_horas_finais'], Decimal('500.00'))
        self.assertEqual(res['kpis']['desvio_horas_abs'], Decimal('400.00')) # 400 horas a mais que o previsto (100)

class EquipamentoProdutividadeServiceTestCase(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(codigo='CLI', nome='Cli')
        self.projeto = Projeto.objects.create(cliente=self.cliente, codigo='PRJ')
        self.equip = Equipamento.objects.create(codigo='EQ', nome='Equip')
        self.pe = ProjetoEquipamento.objects.create(projeto=self.projeto, equipamento=self.equip)
        self.ativ = Atividade.objects.create(codigo='AT', nome='Atividade')
        
        # Setup inicial com 2.5 horas estimadas por unidade
        self.pea = ProjetoEquipamentoAtividade.objects.create(
            projeto_equipamento=self.pe,
            atividade=self.ativ,
            tempo_medio_estimado=2.50
        )
        
        # Grupo e usuário para ter o colaborador necessário pro apontamento
        user = User.objects.create_user(username='tec', password='123')
        self.colab = Colaborador.objects.create(nome='Tec', usuario=user, custo_hora=50.0)

    def test_recalculo_autoajuste_apos_aprovacao(self):
        from operations.services import EquipamentoProdutividadeService
        
        # Apontamento EM_ANALISE (não deve impactar o cálculo)
        apont_em_analise = Apontamento.objects.create(
            projeto=self.projeto, equipamento=self.equip, atividade=self.ativ,
            colaborador=self.colab, data=date.today(),
            horas=5.0, quantidade=1.0, status='EM_ANALISE'
        )
        
        EquipamentoProdutividadeService.recalcular_tempo_medio(self.pea)
        self.pea.refresh_from_db()
        self.assertEqual(self.pea.total_amostras, 0)
        self.assertIsNone(self.pea.tempo_medio_real)

        # Apontamento APROVADO 1 (4h / 2un = 2.0 h/un)
        apont_aprovado1 = Apontamento.objects.create(
            projeto=self.projeto, equipamento=self.equip, atividade=self.ativ,
            colaborador=self.colab, data=date.today(),
            horas=4.0, quantidade=2.0, status='APROVADO'
        )
        
        EquipamentoProdutividadeService.recalcular_tempo_medio(self.pea)
        self.pea.refresh_from_db()
        self.assertEqual(self.pea.total_amostras, 1)
        self.assertEqual(float(self.pea.tempo_medio_real), 2.00)
        
        # Desvio %: Estimado 2.5, Real 2.0. Economia de tempo.
        # Desvio = ((2.0 - 2.5) / 2.5) * 100 = -20%
        self.assertEqual(float(self.pea.desvio_tempo_pct), -20.00)

        # Apontamento APROVADO 2 (14h / 2un = 7.0 h/un)
        apont_aprovado2 = Apontamento.objects.create(
            projeto=self.projeto, equipamento=self.equip, atividade=self.ativ,
            colaborador=self.colab, data=date.today(),
            horas=14.0, quantidade=2.0, status='APROVADO'
        )

        EquipamentoProdutividadeService.recalcular_tempo_medio(self.pea)
        self.pea.refresh_from_db()
        
        # Total de apontamentos: 2
        # Total horas: 18.0
        # Total unid: 4.0
        # Média Real: 18.0 / 4.0 = 4.5 h/un
        self.assertEqual(self.pea.total_amostras, 2)
        self.assertEqual(float(self.pea.tempo_medio_real), 4.50)
        
        # Desvio = ((4.5 - 2.5) / 2.5) * 100 = 80.0%
        self.assertEqual(float(self.pea.desvio_tempo_pct), 80.00)
