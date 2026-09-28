class RLSMixin:
    """
    Mixin para garantir Row Level Security (RLS) nas QuerySets.
    Planejadores veem tudo. Técnicos de Campo veem apenas os registros onde
    o colaborador atrelado ao registro (self.rls_user_field) seja eles mesmos.
    """
    rls_user_field = 'colaborador__usuario'

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        
        if user.is_anonymous:
            return qs.none()
            
        if user.groups.filter(name='Planejador/Analista').exists():
            return qs
            
        # Filtra para o Técnico de Campo
        filter_kwargs = {self.rls_user_field: user}
        return qs.filter(**filter_kwargs)
