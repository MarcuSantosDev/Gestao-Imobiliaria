from apps.imoveis.models import Notificacao


def notificacoes(request):
    if not request.user.is_authenticated:
        return {}
    notificacoes_queryset = Notificacao.objects.filter(
        destinatario=request.user,
        status=Notificacao.STATUS_PENDING,
    ).select_related('remetente', 'demanda').order_by('-criado_em')
    notificacoes_list = notificacoes_queryset[:5]
    return {
        'notifications_count': notificacoes_queryset.count(),
        'notifications_list': notificacoes_list,
    }
