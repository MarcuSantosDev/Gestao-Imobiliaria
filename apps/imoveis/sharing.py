from apps.imoveis.utils import formatar_moeda


def gerar_texto_compartilhamento(imovel):
    linhas = [
        imovel.titulo,
        "",
        f"Local: {imovel.bairro}, {imovel.cidade}",
        f"Valor: {formatar_moeda(imovel.valor)}",
    ]

    if imovel.tipo:
        linhas.append(f"Tipo: {imovel.get_tipo_display()} · {imovel.get_finalidade_display()}")

    caracteristicas = []
    if imovel.dormitorios:
        caracteristicas.append(f"Dormitórios: {imovel.dormitorios}")
    if imovel.suites:
        caracteristicas.append(f"Suítes: {imovel.suites}")
    if imovel.banheiros:
        caracteristicas.append(f"Banheiros: {imovel.banheiros}")
    if imovel.vagas:
        caracteristicas.append(f"Vagas: {imovel.vagas}")

    if caracteristicas:
        linhas.append('')
        linhas.extend(caracteristicas)

    if imovel.posicao_solar:
        linhas.append(f"Posição solar: {imovel.get_posicao_solar_display()}")

    infra = imovel.infraestrutura.all()
    if infra.exists():
        linhas.append('')
        linhas.append('Infraestrutura:')
        for item in infra:
            linhas.append(f"- {item.nome}")

    if imovel.descricao:
        linhas.extend(['', imovel.descricao.strip()])

    return '\n'.join(linhas)
