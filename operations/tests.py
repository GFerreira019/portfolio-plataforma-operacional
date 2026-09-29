from django.test import TestCase
from django.contrib.auth.models import User, Group
from rest_framework.test import APIClient
from catalog.models import Cliente, Projeto, Equipamento, ProjetoEquipamento, Atividade, ProjetoEquipamentoAtividade, Colaborador
from operations.models import Apontamento
from datetime import date

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

