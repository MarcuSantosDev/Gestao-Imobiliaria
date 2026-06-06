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
            default=50,
            help='Quantidade de imóveis a criar (padrão: 50)',
        )

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
            vagas = 0 if sem_quartos else min(dormitorios, 3)

            if finalidade == 'locacao':
                valor = Decimal(str(1800 + n * 150))
            else:
                valor = Decimal(str(280000 + n * 25000))

            tipo_label = dict(Imovel.TIPO_CHOICES).get(tipo, tipo).title()
            titulo = f'{tipo_label} {bairro} #{n + 1}'
            finalizado_em = agora - timedelta(days=n) if status in Imovel.HISTORICO_STATUS else None
            imovel, created = Imovel.objects.get_or_create(
                titulo=titulo,
                defaults={
                    'tipo': tipo,
                    'finalidade': finalidade,
                    'cidade': cidade,
                    'bairro': bairro,
                    'valor': valor,
                    'descricao': f'Imóvel de teste em {bairro}, {cidade}.',
                    'status': status,
                    'dormitorios': dormitorios,
                    'vagas': vagas,
                    'corretor': corretores[n % len(corretores)],
                    'finalizado_em': finalizado_em,
                },
            )
            if created:
                novos += 1
                if infra_list:
                    inicio = n % max(1, len(infra_list) - 2)
                    imovel.infraestrutura.set(infra_list[inicio:inicio + 3])
            imoveis.append(imovel)
        return imoveis, novos

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
                defaults={'telefone': '(83) 98765-4321', 'tipo': 'autonomo'},
            )[0],
            Corretor.objects.get_or_create(
                nome='Carlos Mendes Imóveis',
                defaults={'telefone': '(83) 3333-1111', 'tipo': 'imobiliaria'},
            )[0],
            Corretor.objects.get_or_create(
                nome='Roberto Ferreira',
                defaults={'telefone': '(83) 99876-5432', 'tipo': 'autonomo'},
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
                'vagas': 2,
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
                'vagas': 2,
                'criado_em': agora - timedelta(days=5),
            },
            {
                'cliente': clientes[2],
                'tipo_imovel': 'apartamento',
                'finalidade': 'locacao',
                'status': 'aberta',
                'cidade': 'João Pessoa',
                'bairros': 'Altiplano',
                'valor_minimo': Decimal('2500'),
                'valor_maximo': Decimal('4000'),
                'dormitorios': 2,
                'vagas': 1,
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
                'atendida_em': inicio_mes + timedelta(days=3),
                'criado_em': agora - timedelta(days=20),
            },
            {
                'cliente': clientes[5],
                'tipo_imovel': 'apartamento',
                'finalidade': 'venda',
                'status': 'atendida',
                'cidade': 'João Pessoa',
                'bairros': 'Jardim Oceania',
                'valor_minimo': Decimal('600000'),
                'valor_maximo': Decimal('800000'),
                'dormitorios': 3,
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
                'atendida_em': agora - timedelta(days=45),
                'criado_em': agora - timedelta(days=60),
            },
            {
                'cliente': clientes[7],
                'tipo_imovel': 'comercial',
                'finalidade': 'locacao',
                'status': 'atendida',
                'cidade': 'João Pessoa',
                'bairros': 'Centro',
                'valor_minimo': Decimal('2000'),
                'valor_maximo': Decimal('4000'),
                'atendida_em': inicio_mes + timedelta(days=1),
                'criado_em': agora - timedelta(days=15),
            },
        ]

        demandas_criadas = 0
        for dados in demandas_data:
            bairros = dados['bairros']
            bairro_principal = bairros.split(',')[0].strip()
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
                'vagas': dados.get('vagas'),
                'atendida_em': dados.get('atendida_em'),
            }
            demanda, created = DemandaCliente.objects.get_or_create(**lookup, defaults=defaults)
            if created:
                demandas_criadas += 1
                DemandaCliente.objects.filter(pk=demanda.pk).update(
                    criado_em=dados['criado_em'],
                    atendida_em=dados.get('atendida_em'),
                )
                if infra_list:
                    demanda.infraestrutura.set(infra_list[:2])

        self.stdout.write(self.style.SUCCESS(
            f'Banco populado: {len(corretores)} corretores, {len(clientes)} clientes, '
            f'{imoveis_novos} imóveis novos ({Imovel.objects.count()} no total), '
            f'{demandas_criadas} demandas novas '
            f'({DemandaCliente.objects.filter(status="aberta").count()} abertas, '
            f'{DemandaCliente.objects.filter(status="atendida", atendida_em__year=agora.year, atendida_em__month=agora.month).count()} finalizadas no mês).'
        ))
