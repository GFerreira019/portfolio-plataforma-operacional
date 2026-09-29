from django.db import models
from catalog.models import Projeto, Equipamento, Atividade, Colaborador

class Apontamento(models.Model):
    STATUS_CHOICES = [
        ('EM_ANALISE', 'Em Análise'),
        ('APROVADO', 'Aprovado'),
        ('REJEITADO', 'Rejeitado'),
    ]

    projeto = models.ForeignKey(Projeto, on_delete=models.RESTRICT)
    equipamento = models.ForeignKey(Equipamento, on_delete=models.RESTRICT)
    atividade = models.ForeignKey(Atividade, on_delete=models.RESTRICT)
    colaborador = models.ForeignKey(Colaborador, on_delete=models.RESTRICT)
    
    data = models.DateField()
    horas = models.DecimalField(max_digits=5, decimal_places=2)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Snapshot histórico
    custo_hora = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Snapshot do custo-hora no momento do apontamento")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='EM_ANALISE')
    
    # Auditoria
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    # criado_por será incluído na Fase 3 (Autenticação)

    def __str__(self):
        return f"{self.data} - {self.colaborador.nome} - {self.horas}h"

    @property
    def custo_realizado(self):
        return self.horas * self.custo_hora

    def save(self, *args, **kwargs):
        from django.core.exceptions import ValidationError

        if not self.pk:
            # Snapshot histórico na criação
            if self.colaborador:
                self.custo_hora = self.colaborador.custo_hora
        else:
            # Regra: Bloquear edição de apontamentos se o Status for APROVADO (exceto mudança de status)
            old_instance = Apontamento.objects.get(pk=self.pk)
            if old_instance.status == 'APROVADO':
                # Verifica se outros campos foram alterados além do status
                changed = False
                fields_to_check = ['projeto_id', 'equipamento_id', 'atividade_id', 'colaborador_id', 'data', 'horas', 'quantidade']
                for field in fields_to_check:
                    if getattr(old_instance, field) != getattr(self, field):
                        changed = True
                        break
                
                if changed:
                    raise ValidationError("Não é permitido editar informações de um apontamento já APROVADO.")

        super().save(*args, **kwargs)
