ELEVADOR_NOMES = frozenset({'elevador'})
VARANDA_NOMES = frozenset({'varanda'})


def _normalizar_nome(nome):
    return (nome or '').strip().lower()


def imovel_tem_elevador(imovel):
    if imovel.elevador:
        return True
    return any(
        _normalizar_nome(n) in ELEVADOR_NOMES
        for n in imovel.infraestrutura.values_list('nome', flat=True)
    )


def imovel_tem_varanda(imovel):
    if imovel.varanda:
        return True
    return any(
        _normalizar_nome(n) in VARANDA_NOMES
        for n in imovel.infraestrutura.values_list('nome', flat=True)
    )


def sincronizar_elevador_varanda(imovel):
    nomes = {_normalizar_nome(n) for n in imovel.infraestrutura.values_list('nome', flat=True)}
    imovel.elevador = 'elevador' in nomes
    imovel.varanda = 'varanda' in nomes
