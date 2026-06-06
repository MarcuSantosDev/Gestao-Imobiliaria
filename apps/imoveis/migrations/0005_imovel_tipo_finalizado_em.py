from django.db import migrations, models
from django.utils import timezone


CATEGORIA_PARA_TIPO = {
    'casa': 'casa',
    'apartamento': 'apartamento',
    'cobertura': 'cobertura',
    'terreno': 'terreno',
    'comercial': 'comercial',
    'sala comercial': 'comercial',
    'galpão': 'comercial',
    'galpao': 'comercial',
    'fazenda': 'casa',
    'chácara': 'casa',
    'chacara': 'casa',
    'sítio': 'casa',
    'sitio': 'casa',
}


def migrar_categoria_para_tipo(apps, schema_editor):
    Imovel = apps.get_model('imoveis', 'Imovel')
    Categoria = apps.get_model('imoveis', 'Categoria')
    agora = timezone.now()

    for imovel in Imovel.objects.all():
        tipo = 'apartamento'
        if imovel.categoria_id:
            nome = Categoria.objects.filter(pk=imovel.categoria_id).values_list('nome', flat=True).first()
            if nome:
                tipo = CATEGORIA_PARA_TIPO.get(nome.lower(), 'apartamento')
        imovel.tipo = tipo
        if imovel.status in ('vendido', 'alugado', 'reservado') and not imovel.finalizado_em:
            imovel.finalizado_em = agora
        imovel.save(update_fields=['tipo', 'finalizado_em'])


class Migration(migrations.Migration):

    dependencies = [
        ('imoveis', '0004_demandacliente_atendida_em'),
    ]

    operations = [
        migrations.AddField(
            model_name='imovel',
            name='tipo',
            field=models.CharField(
                choices=[
                    ('casa', 'Casa'),
                    ('apartamento', 'Apartamento'),
                    ('cobertura', 'Cobertura'),
                    ('terreno', 'Terreno'),
                    ('comercial', 'Comercial'),
                ],
                default='apartamento',
                max_length=30,
            ),
        ),
        migrations.AddField(
            model_name='imovel',
            name='finalizado_em',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(migrar_categoria_para_tipo, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='imovel',
            name='categoria',
        ),
        migrations.DeleteModel(
            name='Categoria',
        ),
    ]
