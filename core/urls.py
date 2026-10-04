"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from catalog.views import (
    ClienteViewSet, ProjetoViewSet, EquipamentoViewSet,
    AtividadeViewSet, ColaboradorViewSet, OrcamentoViewSet,
    ProjetoEquipamentoViewSet, ProjetoEquipamentoAtividadeViewSet
)
from operations.views import ApontamentoViewSet

router = DefaultRouter()
router.register(r'clientes', ClienteViewSet)
router.register(r'projetos', ProjetoViewSet)
router.register(r'equipamentos', EquipamentoViewSet)
router.register(r'atividades', AtividadeViewSet)
router.register(r'colaboradores', ColaboradorViewSet)
router.register(r'orcamentos', OrcamentoViewSet)
router.register(r'projeto-equipamentos', ProjetoEquipamentoViewSet)
router.register(r'projeto-equipamento-atividades', ProjetoEquipamentoAtividadeViewSet)
router.register(r'apontamentos', ApontamentoViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]
