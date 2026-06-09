from datetime import timedelta
from decimal import Decimal

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.imoveis.localidades import BAIRROS
from apps.imoveis.models import (
    Cliente,
    Corretor,
    DemandaCliente,
    Imovel,
    Infraestrutura,
)


def _filtros(*chaves):
    return ', '.join(chaves)


class Command(BaseCommand):
    help = 'Popula o banco com dados de teste para desenvolvimento'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Remove clientes, corretores, imóveis e demandas antes de popular',
        )
        parser.add_argument(
            '--imoveis',
            type=int,
            default=200,
            help='Quantidade de imóveis a criar (padrão: 200)',
        )

    def _infra_por_nome(self, infra_list, *nomes):
        por_nome = {i.nome.lower(): i for i in infra_list}
        return [por_nome[n.lower()] for n in nomes if n.lower() in por_nome]

    def _criar_imoveis(self, corretores, infra_list, quantidade):
        tipos = [
            ('apartamento', 'venda'),
            ('casa', 'venda'),
            ('cobertura', 'venda'),
            ('terreno', 'venda'),
            ('comercial', 'locacao'),
            ('apartamento', 'locacao'),
            ('casa', 'locacao'),
        ]
        statuses = ['disponivel', 'disponivel', 'disponivel', 'vendido', 'alugado', 'reservado']
        posicoes = ['nascente', 'sul', 'poente', None]
        cidades = list(BAIRROS.keys())
        agora = timezone.now()

        imoveis = []
        novos = 0
        for n in range(quantidade):
            tipo, finalidade = tipos[n % len(tipos)]
            cidade = cidades[n % len(cidades)]
            bairro = BAIRROS[cidade][n % len(BAIRROS[cidade])]
            status = statuses[n % len(statuses)]
            sem_quartos = tipo in ('terreno', 'comercial')
            dormitorios = 0 if sem_quartos else (n % 4) + 1
            suites = 0 if sem_quartos else min(dormitorios, n % 3)
            banheiros = 0 if sem_quartos else max(1, dormitorios + (n % 2))
            vagas = 0 if sem_quartos else min(dormitorios, 3)
            vagas_cobertas = 0 if sem_quartos else min(vagas, n % 3)
            predio = tipo in ('apartamento', 'cobertura', 'comercial')
            total_andares = (n % 20) + 5 if predio else None
            andar = (n % (total_andares or 1)) + 1 if predio else None
            tem_elevador = predio and (n % 3 != 0)
            tem_varanda = not sem_quartos and (n % 2 == 0)
            posicao_solar = posicoes[n % len(posicoes)]

            if finalidade == 'locacao':
                valor = Decimal(str(1800 + n * 150))
                valor_condominio = Decimal(str(350 + n * 25)) if predio else None
            else:
                valor = Decimal(str(280000 + n * 25000))
                valor_condominio = Decimal(str(450 + n * 30)) if predio else None

            area_construida = None if tipo == 'terreno' else Decimal(str(55 + dormitorios * 18 + n * 3))
            area_total = (
                Decimal(str(200 + n * 15)) if tipo == 'terreno'
                else area_construida + Decimal(str(10 + n % 20))
            )

            tipo_label = dict(Imovel.TIPO_CHOICES).get(tipo, tipo).title()
            titulo = f'{tipo_label} {bairro} #{n + 1}'
            finalizado_em = agora - timedelta(days=n) if status in Imovel.HISTORICO_STATUS else None

            defaults = {
                'tipo': tipo,
                'finalidade': finalidade,
                'cidade': cidade,
                'bairro': bairro,
                'endereco': f'Rua Exemplo, {100 + n}',
                'valor': valor,
                'valor_condominio': valor_condominio,
                'descricao': (
                    f'Imóvel de teste em {bairro}, {cidade}. '
                    f'{dormitorios} dorm., {suites} suíte(s), {banheiros} banheiro(s).'
                ),
                'status': status,
                'dormitorios': dormitorios,
                'suites': suites,
                'banheiros': banheiros,
                'vagas': vagas,
                'vagas_cobertas': vagas_cobertas,
                'area_total': area_total,
                'area_construida': area_construida,
                'total_andares': total_andares,
                'andar': andar,
                'elevador': tem_elevador,
                'varanda': tem_varanda,
                'posicao_solar': posicao_solar,
                'corretor': corretores[n % len(corretores)],
                'finalizado_em': finalizado_em,
            }

            imovel, created = Imovel.objects.update_or_create(
                titulo=titulo,
                defaults=defaults,
            )
            if created:
                novos += 1

            extras = []
            if tem_elevador:
                extras.extend(self._infra_por_nome(infra_list, 'Elevador'))
            if tem_varanda:
                extras.extend(self._infra_por_nome(infra_list, 'Varanda'))
            if vagas_cobertas:
                extras.extend(self._infra_por_nome(infra_list, 'Vagas Cobertas'))
            if n % 2 == 0:
                extras.extend(self._infra_por_nome(infra_list, 'Piscina', 'Academia'))
            if n % 3 == 0:
                extras.extend(self._infra_por_nome(infra_list, 'Portaria 24h', 'Salão de Festas'))
            if extras:
                imovel.infraestrutura.set({i.pk for i in extras})

            imoveis.append(imovel)
        return imoveis, novos

    def _criar_demanda(self, dados, infra_list):
        bairros = dados.get('bairros', '')
        bairro_principal = bairros.split(',')[0].strip() if bairros else None
        lookup = {
            'cliente': dados['cliente'],
            'tipo_imovel': dados['tipo_imovel'],
            'finalidade': dados['finalidade'],
            'cidade': dados['cidade'],
        }
        defaults = {
            'status': dados['status'],
            'bairro': bairro_principal,
            'bairros': bairros,
            'valor_minimo': dados.get('valor_minimo'),
            'valor_maximo': dados.get('valor_maximo'),
            'dormitorios': dados.get('dormitorios'),
            'suites': dados.get('suites'),
            'banheiros': dados.get('banheiros'),
            'area_minima': dados.get('area_minima'),
            'condominio_maximo': dados.get('condominio_maximo'),
            'elevador': dados.get('elevador', 'indiferente'),
            'andar_maximo': dados.get('andar_maximo'),
            'varanda': dados.get('varanda', 'indiferente'),
            'posicao_solar': dados.get('posicao_solar', 'indiferente'),
            'vagas': dados.get('vagas'),
            'vagas_cobertas': dados.get('vagas_cobertas'),
            'filtros_obrigatorios': dados.get('filtros_obrigatorios', ''),
            'atendida_em': dados.get('atendida_em'),
        }
        demanda, created = DemandaCliente.objects.update_or_create(**lookup, defaults=defaults)
        DemandaCliente.objects.filter(pk=demanda.pk).update(
            criado_em=dados['criado_em'],
            atendida_em=dados.get('atendida_em'),
        )
        infra_nomes = dados.get('infraestrutura', [])
        if infra_nomes:
            demanda.infraestrutura.set(self._infra_por_nome(infra_list, *infra_nomes))
        elif created:
            demanda.infraestrutura.clear()
        return demanda, created

    def handle(self, *args, **options):
        if options['clear']:
            DemandaCliente.objects.all().delete()
            Imovel.objects.all().delete()
            Cliente.objects.all().delete()
            Corretor.objects.all().delete()
            self.stdout.write('Dados de teste removidos.')

        call_command('seed_dados')

        infra_list = list(Infraestrutura.objects.all())

        corretores = [
            Corretor.objects.get_or_create(
                nome='Ana Paula Silva',
                defaults={
                    'telefone': '(83) 98765-4321',
                    'creci': '12345-PB',
                    'tipo': 'autonomo',
                },
            )[0],
            Corretor.objects.get_or_create(
                nome='Carlos Mendes Imóveis',
                defaults={
                    'telefone': '(83) 3333-1111',
                    'creci': '54321-PB',
                    'tipo': 'imobiliaria',
                    'imobiliaria': 'Carlos Mendes Imóveis',
                },
            )[0],
            Corretor.objects.get_or_create(
                nome='Roberto Ferreira',
                defaults={
                    'telefone': '(83) 99876-5432',
                    'creci': '67890-PB',
                    'tipo': 'autonomo',
                },
            )[0],
        ]

        clientes_data = [
            ('Maria Oliveira', '(83) 99111-1111', 'maria@email.com'),
            ('João Santos', '(83) 99222-2222', 'joao@email.com'),
            ('Fernanda Lima', '(83) 99333-3333', 'fernanda@email.com'),
            ('Pedro Almeida', '(83) 99444-4444', None),
            ('Juliana Costa', '(83) 99555-5555', 'juliana@email.com'),
            ('Ricardo Souza', '(83) 99666-6666', None),
            ('Camila Rocha', '(83) 99777-7777', 'camila@email.com'),
            ('Lucas Barbosa', '(83) 99888-8888', 'lucas@email.com'),
        ]
        clientes = []
        for nome, telefone, email in clientes_data:
            cliente, _ = Cliente.objects.get_or_create(
                nome=nome,
                defaults={'telefone': telefone, 'email': email},
            )
            clientes.append(cliente)

        imoveis, imoveis_novos = self._criar_imoveis(
            corretores, infra_list, options['imoveis'],
        )

        agora = timezone.now()
        inicio_mes = agora.replace(day=1, hour=10, minute=0, second=0, microsecond=0)

        demandas_data = [
            {
                'cliente': clientes[0],
                'tipo_imovel': 'apartamento',
                'finalidade': 'venda',
                'status': 'aberta',
                'cidade': 'João Pessoa',
                'bairros': 'Manaíra, Tambaú',
                'valor_minimo': Decimal('500000'),
                'valor_maximo': Decimal('700000'),
                'dormitorios': 3,
                'suites': 1,
                'banheiros': 2,
                'area_minima': Decimal('90'),
                'condominio_maximo': Decimal('800'),
                'elevador': 'com',
                'varanda': 'sim',
                'posicao_solar': 'nascente',
                'vagas': 2,
                'vagas_cobertas': 1,
                'filtros_obrigatorios': '',
                'infraestrutura': ['Piscina', 'Academia', 'Portaria 24h'],
                'criado_em': agora - timedelta(days=2),
            },
            {
                'cliente': clientes[1],
                'tipo_imovel': 'casa',
                'finalidade': 'venda',
                'status': 'aberta',
                'cidade': 'João Pessoa',
                'bairros': 'Bessa, Cabo Branco',
                'valor_minimo': Decimal('800000'),
                'valor_maximo': Decimal('1000000'),
                'dormitorios': 4,
                'suites': 2,
                'banheiros': 3,
                'area_minima': Decimal('180'),
                'varanda': 'sim',
                'posicao_solar': 'sul',
                'vagas': 2,
                'vagas_cobertas': 2,
                'filtros_obrigatorios': _filtros(
                    'tipo_imovel', 'finalidade', 'valor', 'dormitorios', 'suites', 'vagas',
                ),
                'infraestrutura': ['Churrasqueira', 'Espaço Gourmet'],
                'criado_em': agora - timedelta(days=5),
            },
            {
                'cliente': clientes[2],
                'tipo_imovel': 'apartamento',
                'finalidade': 'locacao',
                'status': 'aberta',
                'cidade': 'João Pessoa',
                'bairros': 'Altiplano, Bancários',
                'valor_minimo': Decimal('2500'),
                'valor_maximo': Decimal('4000'),
                'dormitorios': 2,
                'banheiros': 1,
                'condominio_maximo': Decimal('600'),
                'elevador': 'indiferente',
                'varanda': 'sim',
                'vagas': 1,
                'filtros_obrigatorios': '',
                'infraestrutura': ['Elevador', 'Portaria 24h'],
                'criado_em': agora - timedelta(days=1),
            },
            {
                'cliente': clientes[3],
                'tipo_imovel': 'terreno',
                'finalidade': 'venda',
                'status': 'aberta',
                'cidade': 'Cabedelo',
                'bairros': 'Intermares, Camboinha',
                'valor_minimo': Decimal('300000'),
                'valor_maximo': Decimal('500000'),
                'area_minima': Decimal('300'),
                'filtros_obrigatorios': _filtros('tipo_imovel', 'valor', 'area_minima'),
                'criado_em': agora - timedelta(days=7),
            },
            {
                'cliente': clientes[4],
                'tipo_imovel': 'cobertura',
                'finalidade': 'venda',
                'status': 'atendida',
                'cidade': 'João Pessoa',
                'bairros': 'Cabo Branco',
                'valor_minimo': Decimal('1000000'),
                'valor_maximo': Decimal('1500000'),
                'dormitorios': 4,
                'suites': 3,
                'banheiros': 4,
                'area_minima': Decimal('200'),
                'condominio_maximo': Decimal('1500'),
                'elevador': 'com',
                'varanda': 'sim',
                'posicao_solar': 'poente',
                'vagas': 3,
                'vagas_cobertas': 2,
                'filtros_obrigatorios': _filtros(
                    'tipo_imovel', 'finalidade', 'valor', 'dormitorios', 'suites',
                    'banheiros', 'area_minima', 'condominio_maximo', 'elevador',
                    'varanda', 'vagas', 'vagas_cobertas', 'infraestrutura',
                ),
                'infraestrutura': ['Piscina', 'Academia', 'Salão de Festas', 'Elevador'],
                'atendida_em': inicio_mes + timedelta(days=3),
                'criado_em': agora - timedelta(days=20),
            },
            {
                'cliente': clientes[5],
                'tipo_imovel': 'apartamento',
                'finalidade': 'venda',
                'status': 'atendida',
                'cidade': 'João Pessoa',
                'bairros': 'Jardim Oceania, Altiplano',
                'valor_minimo': Decimal('600000'),
                'valor_maximo': Decimal('800000'),
                'dormitorios': 3,
                'suites': 1,
                'banheiros': 2,
                'area_minima': Decimal('85'),
                'elevador': 'sem',
                'andar_maximo': 4,
                'varanda': 'indiferente',
                'vagas': 2,
                'filtros_obrigatorios': _filtros(
                    'tipo_imovel', 'valor', 'elevador', 'dormitorios', 'vagas',
                ),
                'infraestrutura': ['Playground', 'Brinquedoteca'],
                'atendida_em': inicio_mes + timedelta(days=10),
                'criado_em': agora - timedelta(days=25),
            },
            {
                'cliente': clientes[6],
                'tipo_imovel': 'casa',
                'finalidade': 'locacao',
                'status': 'atendida',
                'cidade': 'João Pessoa',
                'bairros': 'Bessa',
                'valor_minimo': Decimal('3500'),
                'valor_maximo': Decimal('5000'),
                'dormitorios': 3,
                'banheiros': 2,
                'area_minima': Decimal('120'),
                'varanda': 'sim',
                'vagas': 2,
                'filtros_obrigatorios': '',
                'infraestrutura': ['Churrasqueira'],
                'atendida_em': agora - timedelta(days=45),
                'criado_em': agora - timedelta(days=60),
            },
            {
                'cliente': clientes[7],
                'tipo_imovel': 'comercial',
                'finalidade': 'locacao',
                'status': 'atendida',
                'cidade': 'João Pessoa',
                'bairros': 'Centro, Tambauzinho',
                'valor_minimo': Decimal('2000'),
                'valor_maximo': Decimal('4000'),
                'area_minima': Decimal('40'),
                'elevador': 'com',
                'vagas': 1,
                'filtros_obrigatorios': _filtros('tipo_imovel', 'valor', 'area_minima'),
                'infraestrutura': ['Elevador', 'Coworking'],
                'atendida_em': inicio_mes + timedelta(days=1),
                'criado_em': agora - timedelta(days=15),
            },
        ]

        demandas_criadas = 0
        demandas_atualizadas = 0
        for dados in demandas_data:
            _, created = self._criar_demanda(dados, infra_list)
            if created:
                demandas_criadas += 1
            else:
                demandas_atualizadas += 1

        self.stdout.write(self.style.SUCCESS(
            f'Banco populado: {len(corretores)} corretores, {len(clientes)} clientes, '
            f'{imoveis_novos} imóveis novos ({Imovel.objects.count()} no total), '
            f'{demandas_criadas} demandas novas, {demandas_atualizadas} demandas atualizadas '
            f'({DemandaCliente.objects.filter(status="aberta").count()} abertas, '
            f'{DemandaCliente.objects.filter(status="atendida", atendida_em__year=agora.year, atendida_em__month=agora.month).count()} finalizadas no mês).'
        ))
