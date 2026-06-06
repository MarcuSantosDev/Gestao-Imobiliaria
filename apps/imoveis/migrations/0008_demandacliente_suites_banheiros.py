from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imoveis', '0007_demanda_imovel_campos_busca'),
    ]

    operations = [
        migrations.AddField(
            model_name='demandacliente',
            name='suites',
            field=models.IntegerField(blank=True, null=True, verbose_name='Suítes mínimas'),
        ),
        migrations.AddField(
            model_name='demandacliente',
            name='banheiros',
            field=models.IntegerField(blank=True, null=True, verbose_name='Banheiros mínimos'),
        ),
    ]
