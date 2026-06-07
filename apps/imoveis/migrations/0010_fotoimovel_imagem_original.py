from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imoveis', '0009_demandacliente_filtros_obrigatorios'),
    ]

    operations = [
        migrations.AddField(
            model_name='fotoimovel',
            name='imagem_original',
            field=models.ImageField(
                blank=True,
                help_text='Arquivo original para recorte posterior sem perda de área',
                null=True,
                upload_to='imoveis/originais/',
            ),
        ),
    ]
