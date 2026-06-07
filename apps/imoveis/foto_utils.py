import io
import json
import os

from django.core.files.base import ContentFile
from PIL import Image, ImageOps

JPEG_QUALITY = 95


def parse_recortes(recorte_json):
    if not recorte_json:
        return []
    try:
        dados = json.loads(recorte_json)
    except json.JSONDecodeError:
        return []
    return dados if isinstance(dados, list) else []


def recorte_eh_inteiro(recorte, largura, altura, tolerancia=2):
    if not recorte or not isinstance(recorte, dict):
        return True
    try:
        x = float(recorte.get('x', 0))
        y = float(recorte.get('y', 0))
        w = float(recorte.get('width', largura))
        h = float(recorte.get('height', altura))
    except (TypeError, ValueError):
        return True
    return (
        x <= tolerancia
        and y <= tolerancia
        and w >= largura - tolerancia
        and h >= altura - tolerancia
    )


def abrir_imagem_de_bytes(conteudo):
    img = Image.open(io.BytesIO(conteudo))
    img = ImageOps.exif_transpose(img)
    img.load()
    return img


def aplicar_recorte(img, recorte):
    largura, altura = img.size
    if recorte_eh_inteiro(recorte, largura, altura):
        return img
    x = int(round(float(recorte['x'])))
    y = int(round(float(recorte['y'])))
    direita = int(round(float(recorte['x']) + float(recorte['width'])))
    baixo = int(round(float(recorte['y']) + float(recorte['height'])))
    x = max(0, min(x, largura - 1))
    y = max(0, min(y, altura - 1))
    direita = max(x + 1, min(direita, largura))
    baixo = max(y + 1, min(baixo, altura))
    return img.crop((x, y, direita, baixo))


def salvar_imagem_pil(img, nome_arquivo):
    buffer = io.BytesIO()
    ext = os.path.splitext(nome_arquivo)[1].lower()
    nome_base = os.path.basename(nome_arquivo)

    if ext in ('.png',) and img.mode in ('RGBA', 'LA', 'P'):
        if img.mode == 'P':
            img = img.convert('RGBA')
        img.save(buffer, format='PNG', optimize=True)
        return ContentFile(buffer.getvalue(), nome_base)

    if img.mode not in ('RGB', 'L'):
        img = img.convert('RGB')

    nome_saida = nome_base if ext in ('.jpg', '.jpeg') else f'{os.path.splitext(nome_base)[0]}.jpg'
    img.save(
        buffer,
        format='JPEG',
        quality=JPEG_QUALITY,
        subsampling=0,
        optimize=True,
    )
    return ContentFile(buffer.getvalue(), nome_saida)


def gerar_imagem_exibicao(conteudo_original, nome_arquivo, recorte=None):
    img = abrir_imagem_de_bytes(conteudo_original)
    img = aplicar_recorte(img, recorte)
    return salvar_imagem_pil(img, nome_arquivo)


def gerar_imagem_exibicao_de_arquivo(arquivo_field, recorte=None):
    with arquivo_field.open('rb') as arquivo:
        conteudo = arquivo.read()
    nome = os.path.basename(arquivo_field.name)
    return gerar_imagem_exibicao(conteudo, nome, recorte)
