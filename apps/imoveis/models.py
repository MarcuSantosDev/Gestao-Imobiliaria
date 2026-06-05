from django.db import models

from .localidades import CIDADE_CHOICES

class Cliente(models.Model):
    nome = models.CharField(max_length=150)
    telefone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    observacao = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome
    
class Corretor(models.Model):

    TIPO_CHOICES = [
        ('autonomo', 'Autônomo'),
        ('imobiliaria', 'Imobiliária'),
    ]

    nome = models.CharField(max_length=150)
    telefone = models.CharField(max_length=20)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    observacao = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome
    

class Categoria(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome
    

class Infraestrutura(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome
    

class Imovel(models.Model):

    STATUS_CHOICES = [
        ('disponivel', 'Disponível'),
        ('reservado', 'Reservado'),
        ('vendido', 'Vendido'),
        ('alugado', 'Alugado'),
    ]

    FINALIDADE_CHOICES = [
        ('venda', 'Venda'),
        ('locacao', 'Locação'),
    ]

    POSICAO_SOLAR_CHOICES = [
        ('nascente', 'Nascente'),
        ('sul', 'Sul'),
        ('poente', 'Poente'),
    ]

    titulo = models.CharField(max_length=200)
    categoria = models.ForeignKey('Categoria', on_delete=models.SET_NULL, null=True)
    finalidade = models.CharField(max_length=20, choices=FINALIDADE_CHOICES)

    cidade = models.CharField(max_length=50, choices=CIDADE_CHOICES, default='João Pessoa')
    bairro = models.CharField(max_length=100)
    endereco = models.CharField(max_length=255, blank=True, null=True)

    valor = models.DecimalField(max_digits=12, decimal_places=2)
    valor_condominio = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    descricao = models.TextField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    dormitorios = models.IntegerField(default=0)
    suites = models.IntegerField(default=0)
    banheiros = models.IntegerField(default=0)

    vagas = models.IntegerField(default=0)
    vagas_cobertas = models.IntegerField(default=0)

    area_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    area_construida = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    andar = models.IntegerField(blank=True, null=True)
    elevador = models.BooleanField(default=False)
    varanda = models.BooleanField(default=False)

    posicao_solar = models.CharField(
        max_length=20,
        choices=POSICAO_SOLAR_CHOICES,
        blank=True,
        null=True
    )

    corretor = models.ForeignKey('Corretor', on_delete=models.SET_NULL, null=True)

    infraestrutura = models.ManyToManyField('Infraestrutura', blank=True)

    def __str__(self):
        return self.titulo
    
class FotoImovel(models.Model):
    imovel = models.ForeignKey('Imovel', on_delete=models.CASCADE, related_name='fotos')
    imagem = models.ImageField(upload_to='imoveis/')

    def __str__(self):
        return f"Foto de {self.imovel.titulo}"
    
class DemandaCliente(models.Model):

    TIPO_CHOICES = [
        ('casa', 'Casa'),
        ('apartamento', 'Apartamento'),
        ('cobertura', 'Cobertura'),
        ('terreno', 'Terreno'),
        ('comercial', 'Comercial'),
    ]

    FINALIDADE_CHOICES = [
        ('venda', 'Venda'),
        ('locacao', 'Locação'),
    ]

    STATUS_CHOICES = [
        ('aberta', 'Aberta'),
        ('atendida', 'Finalizada'),
    ]

    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE)

    tipo_imovel = models.CharField(max_length=30, choices=TIPO_CHOICES)
    finalidade = models.CharField(max_length=20, choices=FINALIDADE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberta')

    valor_minimo = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    valor_maximo = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    cidade = models.CharField(max_length=50, choices=CIDADE_CHOICES, default='João Pessoa')
    bairro = models.CharField(max_length=100, blank=True, null=True)
    bairros = models.CharField(max_length=500, blank=True, null=True, help_text='Bairros separados por vírgula')

    dormitorios = models.IntegerField(null=True, blank=True)
    vagas = models.IntegerField(null=True, blank=True)
    posicao_solar = models.CharField(
        max_length=15,
        choices=[
            ('nascente', 'Nascente'),
            ('sul', 'Sul'),
            ('poente', 'Poente'),
            ('indiferente', 'Indiferente'),
        ],
        default='indiferente',
    )

    infraestrutura = models.ManyToManyField('Infraestrutura', blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atendida_em = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.cliente.nome} - {self.tipo_imovel}"

    def get_bairros_lista(self):
        if self.bairros:
            return [b.strip() for b in self.bairros.split(',') if b.strip()]
        if self.bairro:
            return [self.bairro]
        return []