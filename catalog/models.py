from django.db import models
from django.contrib.auth.models import User

class Cliente(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nome = models.CharField(max_length=255)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.codigo} - {self.nome}"

class Projeto(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='projetos')
    codigo = models.CharField(max_length=50)
    ativo = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['cliente', 'codigo'], name='unique_projeto_cliente_codigo')
        ]

    @property
    def nome(self):
        return self.cliente.nome

    def __str__(self):
        return f"{self.codigo} ({self.nome})"

class Equipamento(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nome = models.CharField(max_length=255)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.codigo} - {self.nome}"

class ProjetoEquipamento(models.Model):
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name='equipamentos')
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE, related_name='projetos')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['projeto', 'equipamento'], name='unique_projeto_equipamento')
        ]

    def __str__(self):
        return f"{self.projeto.codigo} - {self.equipamento.codigo}"

class Atividade(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nome = models.CharField(max_length=255)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.codigo} - {self.nome}"

class ProjetoEquipamentoAtividade(models.Model):
    projeto_equipamento = models.ForeignKey(ProjetoEquipamento, on_delete=models.CASCADE, related_name='atividades')
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE, related_name='projetos_equipamentos')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['projeto_equipamento', 'atividade'], name='unique_projeto_equipamento_atividade')
        ]

    def __str__(self):
        return f"{self.projeto_equipamento} - {self.atividade.codigo}"

class Colaborador(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='colaborador')
    nome = models.CharField(max_length=255)
    custo_hora = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

class Orcamento(models.Model):
    projeto = models.OneToOneField(Projeto, on_delete=models.CASCADE, related_name='orcamento')
    horas_previstas = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    quantidade_prevista = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    custo_previsto = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    prazo_previsto = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Orçamento - {self.projeto.codigo}"
