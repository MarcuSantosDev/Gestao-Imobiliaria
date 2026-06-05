from apps.imoveis.utils import formatar_moeda


def gerar_texto_compartilhamento(imovel):
    linhas = [
        f"🏠 {imovel.titulo}",
        "",
        f"📍 {imovel.bairro}, {imovel.cidade}",
        f"💰 {formatar_moeda(imovel.valor)}",
    ]

    if imovel.dormitorios:
        linhas.append(f"🛏 {imovel.dormitorios} quartos")
    if imovel.banheiros:
        linhas.append(f"🚿 {imovel.banheiros} banheiros")
    if imovel.vagas:
        linhas.append(f"🚗 {imovel.vagas} vagas")

    if imovel.posicao_solar:
        linhas.append(f"☀️ {imovel.get_posicao_solar_display()}")

    infra = imovel.infraestrutura.all()
    emoji_map = {
        'Piscina': '🏊 Piscina',
        'Academia': '🏋 Academia',
        'Salão de Festas': '🎉 Salão de Festas',
        'Portaria 24h': '🛡 Portaria 24h',
        'Elevador': '🛗 Elevador',
        'Varanda': '🌿 Varanda',
        'Vagas Cobertas': '🚗 Vagas Cobertas',
    }
    for item in infra:
        linhas.append(emoji_map.get(item.nome, f"✅ {item.nome}"))

    if imovel.corretor:
        linhas.extend([
            "",
            f"👨‍💼 Corretor {imovel.corretor.nome}",
            f"📞 {imovel.corretor.telefone}",
        ])

    return '\n'.join(linhas)
