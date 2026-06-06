from apps.imoveis.infra_utils import imovel_tem_elevador, imovel_tem_varanda
from apps.imoveis.models import Imovel

PONTOS_POR_INFRA = 5
PONTOS_BAIRROS = 30
PONTOS_POSICAO_SOLAR = 20
PONTOS_CRITERIO = 10


def _area_imovel(imovel):
    return imovel.area_total or imovel.area_construida


def _atende_minimo(solicitado, disponivel):
    if solicitado is None:
        return True
    return disponivel >= solicitado


def _atende_valor(demanda, imovel):
    if demanda.valor_minimo is not None and imovel.valor < demanda.valor_minimo:
        return False
    if demanda.valor_maximo is not None and imovel.valor > demanda.valor_maximo:
        return False
    return True


def _tem_criterio_valor(demanda):
    return demanda.valor_minimo is not None or demanda.valor_maximo is not None


def _atende_elevador(demanda, imovel):
    tem_elevador = imovel_tem_elevador(imovel)
    if demanda.elevador == 'com' and not tem_elevador:
        return False
    if demanda.elevador == 'sem':
        if tem_elevador:
            return False
        if demanda.andar_maximo is not None:
            if imovel.andar is None or imovel.andar > demanda.andar_maximo:
                return False
    return True


def _tem_criterio_elevador(demanda):
    return demanda.elevador != 'indiferente'


def _atende_varanda(demanda, imovel):
    tem_varanda = imovel_tem_varanda(imovel)
    if demanda.varanda == 'sim' and not tem_varanda:
        return False
    if demanda.varanda == 'nao' and tem_varanda:
        return False
    return True


def _tem_criterio_varanda(demanda):
    return demanda.varanda != 'indiferente'


def _atende_area(demanda, imovel):
    if demanda.area_minima is None:
        return True
    area = _area_imovel(imovel)
    return area is not None and area >= demanda.area_minima


def _atende_condominio(demanda, imovel):
    if demanda.condominio_maximo is None:
        return True
    return (
        imovel.valor_condominio is not None
        and imovel.valor_condominio <= demanda.condominio_maximo
    )


def _atende_bairros(demanda, imovel):
    bairros = demanda.get_bairros_lista()
    return not bairros or imovel.bairro in bairros


def _tem_criterio_bairros(demanda):
    return bool(demanda.get_bairros_lista())


def _atende_posicao_solar(demanda, imovel):
    if demanda.posicao_solar == 'indiferente':
        return True
    return imovel.posicao_solar and imovel.posicao_solar == demanda.posicao_solar


def _tem_criterio_posicao_solar(demanda):
    return demanda.posicao_solar != 'indiferente'


def _atende_infraestrutura(demanda, imovel):
    infra_desejada = list(demanda.infraestrutura.values_list('id', flat=True))
    if not infra_desejada:
        return True
    infra_imovel = set(imovel.infraestrutura.values_list('id', flat=True))
    return all(infra_id in infra_imovel for infra_id in infra_desejada)


def _pontos_infraestrutura(demanda, imovel):
    infra_desejada = list(demanda.infraestrutura.values_list('id', flat=True))
    if not infra_desejada:
        return 0, 0
    infra_imovel = set(imovel.infraestrutura.values_list('id', flat=True))
    max_pontos = len(infra_desejada) * PONTOS_POR_INFRA
    pontos = sum(PONTOS_POR_INFRA for infra_id in infra_desejada if infra_id in infra_imovel)
    return pontos, max_pontos


_CRITERIOS = {
    'tipo_imovel': (
        lambda d, i: i.tipo == d.tipo_imovel,
        lambda d: True,
        PONTOS_CRITERIO,
    ),
    'finalidade': (
        lambda d, i: i.finalidade == d.finalidade,
        lambda d: True,
        PONTOS_CRITERIO,
    ),
    'cidade': (
        lambda d, i: i.cidade == d.cidade,
        lambda d: True,
        PONTOS_CRITERIO,
    ),
    'valor': (
        _atende_valor,
        _tem_criterio_valor,
        PONTOS_CRITERIO,
    ),
    'dormitorios': (
        lambda d, i: _atende_minimo(d.dormitorios, i.dormitorios),
        lambda d: d.dormitorios is not None,
        PONTOS_CRITERIO,
    ),
    'suites': (
        lambda d, i: _atende_minimo(d.suites, i.suites),
        lambda d: d.suites is not None,
        PONTOS_CRITERIO,
    ),
    'banheiros': (
        lambda d, i: _atende_minimo(d.banheiros, i.banheiros),
        lambda d: d.banheiros is not None,
        PONTOS_CRITERIO,
    ),
    'area_minima': (
        _atende_area,
        lambda d: d.area_minima is not None,
        PONTOS_CRITERIO,
    ),
    'condominio_maximo': (
        _atende_condominio,
        lambda d: d.condominio_maximo is not None,
        PONTOS_CRITERIO,
    ),
    'elevador': (
        _atende_elevador,
        _tem_criterio_elevador,
        PONTOS_CRITERIO,
    ),
    'varanda': (
        _atende_varanda,
        _tem_criterio_varanda,
        PONTOS_CRITERIO,
    ),
    'vagas': (
        lambda d, i: _atende_minimo(d.vagas, i.vagas),
        lambda d: d.vagas is not None,
        PONTOS_CRITERIO,
    ),
    'vagas_cobertas': (
        lambda d, i: _atende_minimo(d.vagas_cobertas, i.vagas_cobertas),
        lambda d: d.vagas_cobertas is not None,
        PONTOS_CRITERIO,
    ),
    'bairros': (
        _atende_bairros,
        _tem_criterio_bairros,
        PONTOS_BAIRROS,
    ),
    'posicao_solar': (
        _atende_posicao_solar,
        _tem_criterio_posicao_solar,
        PONTOS_POSICAO_SOLAR,
    ),
}


def _passa_filtros_obrigatorios(demanda, imovel):
    if imovel.cidade != demanda.cidade:
        return False
    if not _atende_bairros(demanda, imovel):
        return False

    for chave, (atende, tem_criterio, _) in _CRITERIOS.items():
        if chave in ('cidade', 'bairros'):
            continue
        if not demanda.filtro_e_obrigatorio(chave):
            continue
        if not tem_criterio(demanda):
            continue
        if not atende(demanda, imovel):
            return False

    if demanda.filtro_e_obrigatorio('infraestrutura') and not _atende_infraestrutura(demanda, imovel):
        return False

    return True


def calcular_compatibilidade(demanda, imovel):
    pontos = 0
    max_pontos = 0

    for chave, (atende, tem_criterio, peso) in _CRITERIOS.items():
        if chave in ('cidade', 'bairros') or demanda.filtro_e_obrigatorio(chave):
            continue
        if not tem_criterio(demanda):
            continue
        max_pontos += peso
        if atende(demanda, imovel):
            pontos += peso

    if not demanda.filtro_e_obrigatorio('infraestrutura'):
        infra_pontos, infra_max = _pontos_infraestrutura(demanda, imovel)
        pontos += infra_pontos
        max_pontos += infra_max

    if max_pontos == 0:
        return 100
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
