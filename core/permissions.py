from rest_framework import permissions

class IsPlanejadorOrOwner(permissions.BasePermission):
    """
    Permite acesso total a Planejadores/Analistas.
    Técnicos de Campo só podem acessar objetos que pertençam a eles (quando aplicável).
    """

    def has_permission(self, request, view):
        # Todos os usuários autenticados têm permissão geral (a filtragem fina é no get_queryset)
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.groups.filter(name='Planejador/Analista').exists():
            return True
        
        # Se for Técnico, verifica se o objeto pertence ao usuário.
        # Supõe que o objeto tem um atributo 'colaborador' que tem 'usuario'.
        if hasattr(obj, 'colaborador') and obj.colaborador.usuario == request.user:
            return True
            
        return False

class IsPlanejador(permissions.BasePermission):
    """
    Permite acesso apenas a Planejadores/Analistas.
    """
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='Planejador/Analista').exists()
