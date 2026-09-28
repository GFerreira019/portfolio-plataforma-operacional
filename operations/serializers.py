from rest_framework import serializers
from .models import Apontamento

class ApontamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apontamento
        fields = '__all__'
        read_only_fields = ['custo_hora', 'criado_em', 'colaborador']

    def validate(self, data):
        request = self.context.get('request')
        
        # Se for atualização e o status estiver mudando para APROVADO
        if self.instance and 'status' in data and data['status'] == 'APROVADO':
            if request and request.user == self.instance.colaborador.usuario:
                raise serializers.ValidationError(
                    {"status": "Regra de Anti-Autoaprovação: Um planejador não pode aprovar seu próprio apontamento."}
                )
                
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request.user, 'colaborador'):
            validated_data['colaborador'] = request.user.colaborador
        else:
            raise serializers.ValidationError({"colaborador": "Usuário autenticado não possui um colaborador associado."})
            
        return super().create(validated_data)
