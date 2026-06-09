from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.imoveis.fields import MoedaDecimalField
from apps.imoveis.localidades import CIDADES, bairros_da_cidade
from apps.imoveis.models import DemandaCliente, FILTRO_DEMANDA_OPCOES, Imovel, Notificacao


class DemandaForm(forms.ModelForm):
    valor_minimo = MoedaDecimalField(label='Valor mínimo', required=False)
    valor_maximo = MoedaDecimalField(label='Até que valor?', required=False)
    condominio_maximo = MoedaDecimalField(label='Valor máximo de condomínio', required=False)

    bairros_selecionados = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Bairros desejados',
    )

    colaboradores = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.none(),
        required=False,
        widget=forms.SelectMultiple(attrs={'size': '5'}),
        label='Colaboradores',
        help_text='Selecione outros usuários que podem colaborar nesta demanda.',
    )

    filtros_obrigatorios_selecionados = forms.MultipleChoiceField(
        required=False,
        choices=FILTRO_DEMANDA_OPCOES,
        widget=forms.CheckboxSelectMultiple,
        label='Critérios adicionais obrigatórios na busca',
        help_text='Cidade e bairros já são sempre obrigatórios. Marque aqui outros critérios que excluem imóveis da busca.',
    )

    class Meta:
        model = DemandaCliente
        fields = [
            'cliente',
            'tipo_imovel',
            'finalidade',
            'valor_minimo',
            'valor_maximo',
            'cidade',
            'dormitorios',
            'suites',
            'banheiros',
            'area_minima',
            'elevador',
            'andar_maximo',
            'varanda',
            'posicao_solar',
            'condominio_maximo',
            'vagas',
            'vagas_cobertas',
            'infraestrutura',
            'status',
        ]
        widgets = {
            'infraestrutura': forms.CheckboxSelectMultiple,
            'cidade': forms.Select(attrs={'id': 'id_cidade'}),
            'tipo_imovel': forms.Select(attrs={'id': 'id_tipo_imovel'}),
            'elevador': forms.Select(attrs={'id': 'id_elevador'}),
            'area_minima': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'andar_maximo': forms.NumberInput(attrs={'min': '0', 'id': 'id_andar_maximo'}),
            'dormitorios': forms.NumberInput(attrs={'min': '0'}),
            'suites': forms.NumberInput(attrs={'min': '0'}),
            'banheiros': forms.NumberInput(attrs={'min': '0'}),
            'vagas': forms.NumberInput(attrs={'min': '0'}),
            'vagas_cobertas': forms.NumberInput(attrs={'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        cidade = self.data.get('cidade') or (self.instance.cidade if self.instance.pk else '')
        bairros = bairros_da_cidade(cidade)
        self.fields['cidade'].choices = [('', 'Selecione a cidade')] + [(c, c) for c in CIDADES]
        self.fields['bairros_selecionados'].choices = [(b, b) for b in bairros]
        if self.instance and self.instance.bairros:
            self.fields['bairros_selecionados'].initial = self.instance.get_bairros_lista()
        self.fields['filtros_obrigatorios_selecionados'].initial = (
            self.instance.get_filtros_opcionais_obrigatorios_lista() if self.instance.pk else []
        )
        colaboradores_qs = get_user_model().objects.filter(is_superuser=False)
        if self.user is not None:
            colaboradores_qs = colaboradores_qs.exclude(pk=self.user.pk)
        self.fields['colaboradores'].queryset = colaboradores_qs.order_by('username')
        self.fields['colaboradores'].label = 'Convidar novos colaboradores'
        self.fields['colaboradores'].help_text = 'Selecione usuários para convidar. Eles só passam a colaborar após aceitarem o convite.'
        if self.instance and self.instance.pk:
            self.fields['colaboradores'].initial = []
        if not self.instance.pk:
            self.fields.pop('status', None)
        else:
            self.fields['status'].choices = [
                ('aberta', 'Aberta'),
                ('com_proposta', 'Com proposta'),
                ('atendida', 'Finalizada'),
                ('cancelado', 'Cancelada'),
            ]
        self.fields['tipo_imovel'].label = 'Qual tipo de imóvel está procurando?'
        self.fields['finalidade'].label = 'Para locação ou venda?'
        self.fields['vagas'].label = 'Garagem (mínimo)'
        self.fields['vagas_cobertas'].label = 'Garagens cobertas (mínimo)'
        self.fields['area_minima'].label = 'Área mínima (m²)'
        self.fields['andar_maximo'].label = 'Sem elevador — até qual andar?'
        self.fields['suites'].label = 'Suítes (mínimo)'
        self.fields['banheiros'].label = 'Banheiros (mínimo)'

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('cidade'):
            self.add_error('cidade', 'Selecione a cidade.')
        valor_min = cleaned_data.get('valor_minimo')
        valor_max = cleaned_data.get('valor_maximo')
        if valor_min is not None and valor_max is not None and valor_min > valor_max:
            self.add_error('valor_maximo', 'O valor máximo deve ser maior ou igual ao mínimo.')
        elevador = cleaned_data.get('elevador')
        andar_maximo = cleaned_data.get('andar_maximo')
        if elevador == 'sem' and andar_maximo is None:
            self.add_error('andar_maximo', 'Informe o andar máximo aceito para imóveis sem elevador.')
        if elevador != 'sem' and andar_maximo is not None:
            cleaned_data['andar_maximo'] = None
        vagas = cleaned_data.get('vagas')
        vagas_cobertas = cleaned_data.get('vagas_cobertas')
        if vagas_cobertas is not None and vagas is not None and vagas_cobertas > vagas:
            self.add_error('vagas_cobertas', 'Garagens cobertas não pode ser maior que o total de garagem.')

        if self.instance.pk and cleaned_data.get('status') == 'atendida':
            selecionados = self.instance.get_imoveis_selecionados()
            if not selecionados.exists():
                self.add_error('status', 'A demanda não pode ser finalizada sem nenhum imóvel selecionado.')
            elif not selecionados.filter(status__in=Imovel.HISTORICO_STATUS).exists():
                self.add_error('status', 'A demanda só pode ser finalizada quando um imóvel selecionado estiver vendido ou alugado.')

        colaboradores = cleaned_data.get('colaboradores')
        if self.user and colaboradores and self.user in colaboradores:
            self.add_error('colaboradores', 'Você não pode selecionar a si mesmo como colaborador.')

        if colaboradores and colaboradores.filter(is_superuser=True).exists():
            self.add_error('colaboradores', 'Superusuários não podem ser colaboradores.')

        if self.instance.pk and self.instance.owner and colaboradores:
            if self.instance.owner in colaboradores:
                self.add_error('colaboradores', 'O proprietário não pode ser listado como colaborador.')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        bairros = self.cleaned_data.get('bairros_selecionados', [])
        instance.bairros = ', '.join(bairros)
        instance.bairro = bairros[0] if bairros else None
        obrigatorios = self.cleaned_data.get('filtros_obrigatorios_selecionados', [])
        instance.filtros_obrigatorios = ', '.join(obrigatorios)
        if instance.elevador != 'sem':
            instance.andar_maximo = None
        if not instance.pk:
            instance.status = 'aberta'
            instance.atendida_em = None
        elif instance.status in DemandaCliente.STATUS_HISTORICO and not instance.atendida_em:
            instance.atendida_em = timezone.now()
        elif instance.status in DemandaCliente.STATUS_ABERTAS:
            instance.atendida_em = None
        invited_users = self.cleaned_data.get('colaboradores') or []
        if commit:
            instance.save()
            self.save_m2m()
            self._criar_convites(instance, invited_users)
        return instance

    def _criar_convites(self, instance, convidados):
        if not convidados:
            return
        for usuario in convidados:
            if usuario == self.user:
                continue
            if instance.colaboradores.filter(pk=usuario.pk).exists():
                continue
            if Notificacao.objects.filter(
                destinatario=usuario,
                demanda=instance,
                tipo=Notificacao.TIPO_CONVITE_COLABORADOR,
                status=Notificacao.STATUS_PENDING,
            ).exists():
                continue
            Notificacao.objects.create(
                destinatario=usuario,
                remetente=self.user,
                demanda=instance,
                tipo=Notificacao.TIPO_CONVITE_COLABORADOR,
                mensagem=f'{self.user.username} convidou você para colaborar na demanda de {instance.cliente.nome}.',
            )
