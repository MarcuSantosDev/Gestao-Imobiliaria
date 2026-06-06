from django.core.management.base import BaseCommand

from apps.imoveis.models import Infraestrutura


class Command(BaseCommand):
    help = 'Popula infraestruturas iniciais do sistema'

    def handle(self, *args, **options):
        infraestruturas = [
            'Piscina', 'Academia', 'Salão de Festas', 'Salão de Jogos',
            'Espaço Gourmet', 'Churrasqueira', 'Playground', 'Brinquedoteca',
            'Quadra Poliesportiva', 'Coworking', 'Portaria 24h',
            'Elevador', 'Varanda', 'Vagas Cobertas',
        ]

        for nome in infraestruturas:
            Infraestrutura.objects.get_or_create(nome=nome)

        self.stdout.write(self.style.SUCCESS('Dados iniciais cadastrados com sucesso.'))
