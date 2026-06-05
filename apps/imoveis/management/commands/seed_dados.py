from django.core.management.base import BaseCommand

from apps.imoveis.models import Categoria, Infraestrutura


class Command(BaseCommand):
    help = 'Popula categorias e infraestruturas iniciais do sistema'

    def handle(self, *args, **options):
        categorias = [
            'Casa', 'Apartamento', 'Cobertura', 'Terreno', 'Comercial',
            'Sala Comercial', 'Galpão', 'Fazenda', 'Chácara', 'Sítio',
        ]
        infraestruturas = [
            'Piscina', 'Academia', 'Salão de Festas', 'Salão de Jogos',
            'Espaço Gourmet', 'Churrasqueira', 'Playground', 'Brinquedoteca',
            'Quadra Poliesportiva', 'Coworking', 'Portaria 24h',
            'Elevador', 'Varanda', 'Vagas Cobertas',
        ]

        for nome in categorias:
            Categoria.objects.get_or_create(nome=nome)

        for nome in infraestruturas:
            Infraestrutura.objects.get_or_create(nome=nome)

        self.stdout.write(self.style.SUCCESS('Dados iniciais cadastrados com sucesso.'))
