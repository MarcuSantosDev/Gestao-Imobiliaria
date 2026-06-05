BAIRROS = {
    "João Pessoa": [
        "Jardim Cidade Universitária", "Aeroclube", "Altiplano", "Altiplano Cabo Branco",
        "Alto do Céu", "Alto do Mateus", "Amazônia Park", "Anatólia", "Areia Dourada",
        "Bairro das Indústrias", "Bairro dos Ipês", "Bairro dos Novaes", "Bairro dos Novais",
        "Bancários", "Barra de Gramame", "Bessa", "Brisamar", "Cabo Branco", "Castelo Branco",
        "Centro", "Cidade Universitária", "Cidade dos Colibris", "Conjunto Esplanada",
        "Conjunto Joao Agripino", "Conjunto Pedro Gondim", "Costa do Sol", "Costa e Silva",
        "Cristo Redentor", "Cruz das Armas", "Cuiá", "Distrito Industrial", "Enseada de Jacumã",
        "Ernani Sátiro", "Ernesto Geisel", "Esplanada", "Estados", "Expedicionários",
        "Funcionários", "Funcionários II", "Geisel", "Gramame", "Grotão", "Ilha do Bispo",
        "Indústrias", "Ipês", "Jacarapé", "Jaguaribe", "Jardim 13 de Maio",
        "Jardim Luna", "Jardim Oceania", "Jardim São Paulo",
        "Jardim Veneza", "Jardim das Acácias", "Jose Americo Almeida", "José Américo",
        "José Américo de Almeida", "João Agripino", "João Paulo II", "Loteamento Praia Grande",
        "Manaíra", "Mandacarú", "Mangabeira", "Mangabeira II", "Mangabeira III", "Mangabeira IV",
        "Mangabeira V", "Mangabeira VI", "Mangabeira VII", "Mangabeira VIII", "Manguinhos",
        "Mata do Buraquinho", "Miramar", "Mumbaba", "Mussuré", "Muçumagro", "Nova Mangabeira",
        "Novo Milênio", "Oitizeiro", "Padre Zé", "Paratibe", "Pedro Gondim", "Penha",
        "Planalto Boa Esperança", "Planalto da Boa Esperança", "Ponta do Seixas", "Portal do Sol",
        "Poço", "Praia do Seixas", "Quadramares", "Rangel", "Roger", "São José", "Tambauzinho",
        "Tambaú", "Tambiá", "Torre", "Treze de Maio", "Trincheiras", "Valentina",
        "Valentina de Figueiredo", "Varadouro", "Varjão", "Água Fria",
    ],
    "Cabedelo": [
        "Amazônia Park", "Areia Dourada", "Bela Vista II", "Camboinha",
        "Camboinha II", "Camboinha III", "Centro", "Formosa", "Intermares", "Jacaré",
        "Jardim Alfa", "Jardim Brasília", "Jardim Camboinha", "Jardim Jerico",
        "Loteamento Bela Vista", "Loteamento Joao Paulo", "Loteamento Leonor",
        "Loteamento Praia Grande", "Monte Castelo", "Ponta de Campina", "Ponta de Mato",
        "Ponta de Matos", "Portal do Poço", "Poço", "Praia Do Jacare", "Praia Formosa",
        "Praia Santa Catarina", "Recanto Poço", "Recanto do Poço", "Renascer",
        "Santa Catarina", "Vila Sao Joao",
    ],
}

CIDADES = list(BAIRROS.keys())
CIDADE_CHOICES = [(cidade, cidade) for cidade in CIDADES]


def bairros_da_cidade(cidade):
    vistos = set()
    resultado = []
    for bairro in BAIRROS.get(cidade, []):
        if bairro not in vistos:
            vistos.add(bairro)
            resultado.append(bairro)
    return resultado
