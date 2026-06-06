from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imoveis', '0008_demandacliente_suites_banheiros'),
    ]

    operations = [
        migrations.AddField(
            model_name='demandacliente',
            name='filtros_obrigatorios',
            field=models.CharField(
                blank=True,
                help_text='Critérios obrigatórios na busca inteligente, separados por vírgula',
                max_length=500,
            ),
        ),
    ]
