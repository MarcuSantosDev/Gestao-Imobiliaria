from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imoveis', '0006_alter_demandacliente_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='imovel',
            name='total_andares',
            field=models.IntegerField(blank=True, null=True, verbose_name='Total de andares do prédio'),
        ),
        migrations.AddField(
            model_name='demandacliente',
            name='area_minima',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='demandacliente',
            name='elevador',
            field=models.CharField(
                choices=[('indiferente', 'Indiferente'), ('com', 'Com elevador'), ('sem', 'Sem elevador')],
                default='indiferente',
                max_length=15,
            ),
        ),
        migrations.AddField(
            model_name='demandacliente',
            name='andar_maximo',
            field=models.IntegerField(blank=True, null=True, verbose_name='Andar máximo (sem elevador)'),
        ),
        migrations.AddField(
            model_name='demandacliente',
            name='varanda',
            field=models.CharField(
                choices=[('indiferente', 'Indiferente'), ('sim', 'Com varanda'), ('nao', 'Sem varanda')],
                default='indiferente',
                max_length=15,
            ),
        ),
        migrations.AddField(
            model_name='demandacliente',
            name='condominio_maximo',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='demandacliente',
            name='vagas_cobertas',
            field=models.IntegerField(blank=True, null=True, verbose_name='Vagas cobertas mínimas'),
        ),
    ]
