from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('imoveis', '0012_corretor_creci_demanda_carrinho_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='demandacliente',
            name='owner',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='demandas',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
