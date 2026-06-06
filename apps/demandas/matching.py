from apps.imoveis.models import Imovel

PONTOS_POR_INFRA = 5


def _tipo_compativel(demanda, imovel):
    return imovel.tipo == demanda.tipo_imovel


def _atende_minimo(solicitado, disponivel):
    """Quartos/vagas: imóvel precisa ter igual ou mais que o pedido na demanda."""
    if solicitado is None:
        return True
    return disponivel >= solicitado


def _passa_filtros_obrigatorios(demanda, imovel):
    if imovel.finalidade != demanda.finalidade:
        return False

    if demanda.valor_minimo is not None and imovel.valor < demanda.valor_minimo:
        return False
    if demanda.valor_maximo is not None and imovel.valor > demanda.valor_maximo:
        return False

    if imovel.cidade != demanda.cidade:
        return False

    return True


def calcular_compatibilidade(demanda, imovel):
    pontos = 0
    max_pontos = 0

    max_pontos += 15
    if _tipo_compativel(demanda, imovel):
        pontos += 15

    bairros = demanda.get_bairros_lista()
    max_pontos += 15
    if not bairros or imovel.bairro in bairros:
        pontos += 15

    max_pontos += 10
    if _atende_minimo(demanda.dormitorios, imovel.dormitorios):
        pontos += 10

    max_pontos += 10
    if _atende_minimo(demanda.vagas, imovel.vagas):
        pontos += 10

    max_pontos += 10
    if demanda.posicao_solar == 'indiferente' or (
        imovel.posicao_solar and imovel.posicao_solar == demanda.posicao_solar
    ):
        pontos += 10

    infra_desejada = list(demanda.infraestrutura.values_list('id', flat=True))
    if infra_desejada:
        max_pontos += len(infra_desejada) * PONTOS_POR_INFRA
        infra_imovel = set(imovel.infraestrutura.values_list('id', flat=True))
        for infra_id in infra_desejada:
            if infra_id in infra_imovel:
                pontos += PONTOS_POR_INFRA

    if max_pontos == 0:
        return 0
    return int((pontos / max_pontos) * 100)


def buscar_imoveis_compativeis(demanda, min_compatibilidade=0):
    resultados = []
    imoveis = Imovel.objects.filter(status='disponivel').select_related(
        'corretor'
    ).prefetch_related('infraestrutura')

    for imovel in imoveis:
        if not _passa_filtros_obrigatorios(demanda, imovel):
            continue
        compat = calcular_compatibilidade(demanda, imovel)
        if compat >= min_compatibilidade:
            resultados.append({'imovel': imovel, 'compatibilidade': compat})

    resultados.sort(key=lambda item: item['compatibilidade'], reverse=True)
    return resultados
