from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('imoveis', '0011_alter_imovel_andar'),
    ]

    operations = [
        migrations.AddField(
            model_name='corretor',
            name='creci',
            field=models.CharField(default='N/A', max_length=20, verbose_name='CRECI'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='corretor',
            name='imobiliaria',
            field=models.CharField(
                blank=True,
                help_text='Obrigatório quando o corretor é vinculado a uma imobiliária',
                max_length=150,
                null=True,
                verbose_name='Imobiliária',
            ),
        ),
        migrations.AlterField(
            model_name='demandacliente',
            name='status',
            field=models.CharField(
                choices=[
                    ('aberta', 'Aberta'),
                    ('com_proposta', 'Com proposta'),
                    ('atendida', 'Finalizada'),
                    ('cancelado', 'Cancelada'),
                ],
                default='aberta',
                max_length=20,
            ),
        ),
        migrations.CreateModel(
            name='DemandaImovelSelecionado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('adicionado_em', models.DateTimeField(auto_now_add=True)),
                ('demanda', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='imoveis_selecionados',
                    to='imoveis.demandacliente',
                )),
                ('imovel', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='selecoes_demanda',
                    to='imoveis.imovel',
                )),
            ],
            options={
                'ordering': ['-adicionado_em'],
            },
        ),
        migrations.AddConstraint(
            model_name='demandaimovelselecionado',
            constraint=models.UniqueConstraint(
                fields=('demanda', 'imovel'),
                name='demanda_imovel_unico',
            ),
        ),
    ]
