from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('imoveis', '0013_add_demanda_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='imovel',
            name='created_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='imoveis',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
