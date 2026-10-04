from rest_framework import serializers
from .models import (Cliente, Projeto, Equipamento, Atividade, 
                     Colaborador, Orcamento, ProjetoEquipamento, 
                     ProjetoEquipamentoAtividade)

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

class ProjetoSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.CharField(source='cliente.nome', read_only=True)
    
    class Meta:
        model = Projeto
        fields = ['id', 'codigo', 'ativo', 'cliente', 'cliente_nome']

class EquipamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipamento
        fields = '__all__'

class AtividadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Atividade
        fields = '__all__'

class ColaboradorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Colaborador
        fields = '__all__'

class OrcamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orcamento
        fields = '__all__'

class ProjetoEquipamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjetoEquipamento
        fields = '__all__'

class ProjetoEquipamentoAtividadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjetoEquipamentoAtividade
        fields = '__all__'
