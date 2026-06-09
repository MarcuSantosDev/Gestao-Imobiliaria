from django.conf import settings
from django.db import models
from django.utils import timezone

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
    creci = models.CharField(max_length=20, verbose_name='CRECI')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    imobiliaria = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name='Imobiliária',
        help_text='Obrigatório quando o corretor é vinculado a uma imobiliária',
    )
    observacao = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome
    

class Infraestrutura(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome
    

class Imovel(models.Model):

    TIPO_CHOICES = [
        ('casa', 'Casa'),
        ('apartamento', 'Apartamento'),
        ('cobertura', 'Cobertura'),
        ('terreno', 'Terreno'),
        ('comercial', 'Comercial'),
    ]

    HISTORICO_STATUS = ('vendido', 'alugado', 'reservado')

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
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES, default='apartamento')
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

    vagas = models.IntegerField(default=0, verbose_name='Garagem')
    vagas_cobertas = models.IntegerField(default=0, verbose_name='Garagens cobertas')

    area_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    area_construida = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    total_andares = models.IntegerField(blank=True, null=True, verbose_name='Total de andares do prédio')
    andar = models.IntegerField(blank=True, null=True, verbose_name='Andar do imóvel')
    elevador = models.BooleanField(default=False)
    varanda = models.BooleanField(default=False)

    posicao_solar = models.CharField(
        max_length=20,
        choices=POSICAO_SOLAR_CHOICES,
        blank=True,
        null=True
    )

    corretor = models.ForeignKey('Corretor', on_delete=models.SET_NULL, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='imoveis',
    )

    infraestrutura = models.ManyToManyField('Infraestrutura', blank=True)

    finalizado_em = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        if self.status in self.HISTORICO_STATUS:
            if not self.finalizado_em:
                self.finalizado_em = timezone.now()
        elif self.status == 'disponivel':
            self.finalizado_em = None
        super().save(*args, **kwargs)
    
class FotoImovel(models.Model):
    imovel = models.ForeignKey('Imovel', on_delete=models.CASCADE, related_name='fotos')
    imagem = models.ImageField(upload_to='imoveis/')
    imagem_original = models.ImageField(
        upload_to='imoveis/originais/',
        blank=True,
        null=True,
        help_text='Arquivo original para recorte posterior sem perda de área',
    )

    def __str__(self):
        return f"Foto de {self.imovel.titulo}"

    def url_para_recorte(self):
        if self.imagem_original:
            return self.imagem_original.url
        return self.imagem.url

    def _tamanho_arquivo(self, arquivo):
        try:
            return arquivo.size if arquivo else 0
        except (OSError, ValueError):
            return 0

    def arquivo_download(self):
        if self.imagem_original and self._tamanho_arquivo(self.imagem_original) > 0:
            return self.imagem_original
        if self.imagem and self._tamanho_arquivo(self.imagem) > 0:
            return self.imagem
        return None

    def excluir_arquivos_midia(self):
        for campo in ('imagem', 'imagem_original'):
            arquivo = getattr(self, campo, None)
            if arquivo and arquivo.name:
                arquivo.delete(save=False)

    def delete(self, *args, **kwargs):
        self.excluir_arquivos_midia()
        super().delete(*args, **kwargs)

FILTROS_OBRIGATORIOS_FIXOS = ('cidade', 'bairros')

DEFAULT_FILTROS_OBRIGATORIOS = list(FILTROS_OBRIGATORIOS_FIXOS)

FILTRO_DEMANDA_CHOICES = [
    ('tipo_imovel', 'Tipo de imóvel'),
    ('finalidade', 'Finalidade'),
    ('cidade', 'Cidade'),
    ('valor', 'Faixa de valor'),
    ('dormitorios', 'Dormitórios'),
    ('suites', 'Suítes'),
    ('banheiros', 'Banheiros'),
    ('area_minima', 'Área mínima'),
    ('condominio_maximo', 'Condomínio máximo'),
    ('elevador', 'Elevador'),
    ('varanda', 'Varanda'),
    ('vagas', 'Garagem'),
    ('vagas_cobertas', 'Garagens cobertas'),
    ('bairros', 'Bairros'),
    ('posicao_solar', 'Posição solar'),
    ('infraestrutura', 'Infraestrutura'),
]

FILTRO_DEMANDA_OPCOES = [
    (chave, label) for chave, label in FILTRO_DEMANDA_CHOICES
    if chave not in FILTROS_OBRIGATORIOS_FIXOS
]


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
        ('com_proposta', 'Com proposta'),
        ('atendida', 'Finalizada'),
        ('cancelado', 'Cancelada'),
    ]

    STATUS_ABERTAS = ('aberta', 'com_proposta')
    STATUS_HISTORICO = ('atendida', 'cancelado')

    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='demandas',
    )

    tipo_imovel = models.CharField(max_length=30, choices=TIPO_CHOICES)
    finalidade = models.CharField(max_length=20, choices=FINALIDADE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberta')

    valor_minimo = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    valor_maximo = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    cidade = models.CharField(max_length=50, choices=CIDADE_CHOICES, default='João Pessoa')
    bairro = models.CharField(max_length=100, blank=True, null=True)
    bairros = models.CharField(max_length=500, blank=True, null=True, help_text='Bairros separados por vírgula')

    dormitorios = models.IntegerField(null=True, blank=True)
    suites = models.IntegerField(null=True, blank=True, verbose_name='Suítes mínimas')
    banheiros = models.IntegerField(null=True, blank=True, verbose_name='Banheiros mínimos')
    area_minima = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    ELEVADOR_CHOICES = [
        ('indiferente', 'Indiferente'),
        ('com', 'Com elevador'),
        ('sem', 'Sem elevador'),
    ]
    elevador = models.CharField(max_length=15, choices=ELEVADOR_CHOICES, default='indiferente')
    andar_maximo = models.IntegerField(null=True, blank=True, verbose_name='Andar máximo (sem elevador)')

    VARANDA_CHOICES = [
        ('indiferente', 'Indiferente'),
        ('sim', 'Com varanda'),
        ('nao', 'Sem varanda'),
    ]
    varanda = models.CharField(max_length=15, choices=VARANDA_CHOICES, default='indiferente')

    condominio_maximo = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    vagas = models.IntegerField(null=True, blank=True, verbose_name='Garagem mínima')
    vagas_cobertas = models.IntegerField(null=True, blank=True, verbose_name='Garagens cobertas mínimas')

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

    filtros_obrigatorios = models.CharField(
        max_length=500,
        blank=True,
        help_text='Critérios obrigatórios na busca inteligente, separados por vírgula',
    )

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

    def get_bairros_resumo(self, limite=3):
        bairros = self.get_bairros_lista()
        if not bairros:
            return ''
        if len(bairros) <= limite:
            return ', '.join(bairros)
        extras = len(bairros) - limite
        return f"{', '.join(bairros[:limite])} (+{extras})"

    def get_filtros_opcionais_obrigatorios_lista(self):
        if not self.filtros_obrigatorios:
            return []
        fixos = set(FILTROS_OBRIGATORIOS_FIXOS)
        return [
            f.strip() for f in self.filtros_obrigatorios.split(',')
            if f.strip() and f.strip() not in fixos
        ]

    def get_filtros_obrigatorios_lista(self):
        return list(FILTROS_OBRIGATORIOS_FIXOS) + self.get_filtros_opcionais_obrigatorios_lista()

    def filtro_e_obrigatorio(self, chave):
        if chave in FILTROS_OBRIGATORIOS_FIXOS:
            return True
        return chave in self.get_filtros_opcionais_obrigatorios_lista()

    def get_filtros_compatibilidade_lista(self):
        opcionais_obrigatorios = set(self.get_filtros_opcionais_obrigatorios_lista())
        return [
            chave for chave, _ in FILTRO_DEMANDA_OPCOES
            if chave not in opcionais_obrigatorios
        ]

    def _labels_filtros(self, chaves):
        labels = dict(FILTRO_DEMANDA_CHOICES)
        return [labels[chave] for chave in chaves if chave in labels]

    def get_filtros_obrigatorios_labels(self):
        return self._labels_filtros(self.get_filtros_obrigatorios_lista())

    def get_filtros_compatibilidade_labels(self):
        return self._labels_filtros(self.get_filtros_compatibilidade_lista())

    def esta_aberta(self):
        return self.status in self.STATUS_ABERTAS

    def esta_no_historico(self):
        return self.status in self.STATUS_HISTORICO

    def get_imoveis_selecionados(self):
        return Imovel.objects.filter(
            selecoes_demanda__demanda=self,
        ).order_by('-selecoes_demanda__adicionado_em')

    def tem_imovel_vendido_ou_alugado(self):
        return self.get_imoveis_selecionados().filter(status__in=Imovel.HISTORICO_STATUS).exists()


class DemandaImovelSelecionado(models.Model):
    demanda = models.ForeignKey(
        'DemandaCliente',
        on_delete=models.CASCADE,
        related_name='imoveis_selecionados',
    )
    imovel = models.ForeignKey(
        'Imovel',
        on_delete=models.CASCADE,
        related_name='selecoes_demanda',
    )
    adicionado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-adicionado_em']
        constraints = [
            models.UniqueConstraint(
                fields=('demanda', 'imovel'),
                name='demanda_imovel_unico',
            ),
        ]

    def __str__(self):
        return f'{self.demanda} — {self.imovel}'