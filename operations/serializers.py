from rest_framework import serializers
from .models import Apontamento

class ApontamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apontamento
        fields = '__all__'
        read_only_fields = ['custo_hora', 'criado_em', 'colaborador']

    def validate(self, data):
        from catalog.models import ProjetoEquipamentoAtividade
        request = self.context.get('request')
        
        # Se for atualização e o status estiver mudando para APROVADO
        if self.instance and 'status' in data and data['status'] == 'APROVADO':
            if request and request.user == self.instance.colaborador.usuario:
                raise serializers.ValidationError(
                    {"status": "Regra de Anti-Autoaprovação: Um planejador não pode aprovar seu próprio apontamento."}
                )
                
        # Regra: Bloquear edição se já estiver APROVADO (a não ser que esteja mudando o status)
        if self.instance and self.instance.status == 'APROVADO':
            fields_to_check = ['projeto', 'equipamento', 'atividade', 'data', 'horas', 'quantidade']
            for field in fields_to_check:
                if field in data and data[field] != getattr(self.instance, field):
                    raise serializers.ValidationError(
                        {"non_field_errors": "Não é permitido editar informações de um apontamento já APROVADO."}
                    )
        
        # Validar combinação de Projeto, Equipamento e Atividade
        projeto = data.get('projeto', getattr(self.instance, 'projeto', None))
        equipamento = data.get('equipamento', getattr(self.instance, 'equipamento', None))
        atividade = data.get('atividade', getattr(self.instance, 'atividade', None))

        if projeto and equipamento and atividade:
            if not ProjetoEquipamentoAtividade.objects.filter(
                projeto_equipamento__projeto=projeto,
                projeto_equipamento__equipamento=equipamento,
                atividade=atividade
            ).exists():
                raise serializers.ValidationError(
                    {"non_field_errors": "A combinação de Projeto, Equipamento e Atividade não possui vínculo pré-cadastrado no catálogo."}
                )
                
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request.user, 'colaborador'):
            validated_data['colaborador'] = request.user.colaborador
        else:
            raise serializers.ValidationError({"colaborador": "Usuário autenticado não possui um colaborador associado."})
            
        return super().create(validated_data)
