from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import FotoImovel, Imovel


@receiver(pre_delete, sender=FotoImovel)
def limpar_midia_foto(sender, instance, **kwargs):
    instance.excluir_arquivos_midia()


@receiver(pre_delete, sender=Imovel)
def limpar_midia_fotos_imovel(sender, instance, **kwargs):
    for foto in instance.fotos.all():
        foto.excluir_arquivos_midia()
