from apps.imoveis.models import Imovel

TIPO_CATEGORIA_MAP = {
    'casa': ['casa'],
    'apartamento': ['apartamento'],
    'cobertura': ['cobertura'],
    'terreno': ['terreno'],
    'comercial': ['comercial', 'sala comercial', 'galpão', 'galpao'],
}


def _tipo_compativel(demanda, imovel):
    if not imovel.categoria:
        return False
    nomes = TIPO_CATEGORIA_MAP.get(demanda.tipo_imovel, [])
    return imovel.categoria.nome.lower() in nomes


def _passa_filtros_obrigatorios(demanda, imovel):
    if imovel.finalidade != demanda.finalidade:
        return False

    if not _tipo_compativel(demanda, imovel):
        return False

    if demanda.valor_minimo is not None and imovel.valor < demanda.valor_minimo:
        return False
    if demanda.valor_maximo is not None and imovel.valor > demanda.valor_maximo:
        return False

    if imovel.cidade != demanda.cidade:
        return False

    bairros = demanda.get_bairros_lista()
    if not bairros or imovel.bairro not in bairros:
        return False

    return True


def calcular_compatibilidade(demanda, imovel):
    pontos = 0
    max_pontos = 0

    max_pontos += 10
    if demanda.dormitorios is None or imovel.dormitorios >= demanda.dormitorios:
        pontos += 10

    max_pontos += 10
    if demanda.vagas is None or imovel.vagas >= demanda.vagas:
        pontos += 10

    max_pontos += 10
    if demanda.posicao_solar == 'indiferente' or (
        imovel.posicao_solar and imovel.posicao_solar == demanda.posicao_solar
    ):
        pontos += 10

    infra_desejada = set(demanda.infraestrutura.values_list('id', flat=True))
    max_pontos += 70
    if not infra_desejada:
        pontos += 70
    else:
        infra_imovel = set(imovel.infraestrutura.values_list('id', flat=True))
        if infra_desejada.issubset(infra_imovel):
            pontos += 70
        else:
            pontos += int(70 * len(infra_desejada & infra_imovel) / len(infra_desejada))

    if max_pontos == 0:
        return 0
    return int((pontos / max_pontos) * 100)


def buscar_imoveis_compativeis(demanda, min_compatibilidade=0):
    resultados = []
    imoveis = Imovel.objects.filter(status='disponivel').select_related(
        'categoria', 'corretor'
    ).prefetch_related('infraestrutura')

    for imovel in imoveis:
        if not _passa_filtros_obrigatorios(demanda, imovel):
            continue
        compat = calcular_compatibilidade(demanda, imovel)
        if compat >= min_compatibilidade:
            resultados.append({'imovel': imovel, 'compatibilidade': compat})

    resultados.sort(key=lambda item: item['compatibilidade'], reverse=True)
    return resultados
