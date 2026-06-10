import os
import re
from html import unescape
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'


def _download_url(url, timeout=15):
    request = Request(url, headers={'User-Agent': USER_AGENT})
    with urlopen(request, timeout=timeout) as response:
        content_type = response.headers.get_content_charset() or 'utf-8'
        raw = response.read()
        return raw.decode(content_type, errors='ignore')


def _clean_text(html_text):
    text = re.sub(r'<script[^>]*>.*?</script>', ' ', html_text, flags=re.S | re.I)
    text = re.sub(r'<style[^>]*>.*?</style>', ' ', text, flags=re.S | re.I)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return unescape(text).strip()


def _extract_meta(html, key):
    pattern = rf'<meta[^>]+(?:property|name)=["\']{re.escape(key)}["\'][^>]+content=["\']([^"\']+)["\']'
    match = re.search(pattern, html, flags=re.I)
    return unescape(match.group(1).strip()) if match else None


def _extract_tag_text(html, tag):
    pattern = rf'<{tag}[^>]*>(.*?)</{tag}>'
    match = re.search(pattern, html, flags=re.I | re.S)
    if not match:
        return None
    return _clean_text(match.group(1))


def _extract_html_section(html, start_marker, end_marker='</div>'):
    start = html.lower().find(start_marker.lower())
    if start == -1:
        return None

    open_tag = '<div'
    pos = html.find(open_tag, start)
    if pos == -1:
        return None

    depth = 0
    i = pos
    length = len(html)
    while i < length:
        next_open = html.find(open_tag, i)
        next_close = html.find(end_marker, i)
        if next_close == -1:
            break
        if next_open != -1 and next_open < next_close:
            depth += 1
            i = next_open + len(open_tag)
        else:
            depth -= 1
            i = next_close + len(end_marker)
            if depth == 0:
                return html[pos:i]
    return html[pos:]


def _extract_image_urls(html, base_url):
    gallery_section = _extract_html_section(html, 'id="cont-fotos"')
    if not gallery_section and 'galeria_completa' in html.lower():
        gallery_section = _extract_html_section(html, 'class="galeria_completa"')

    source_html = gallery_section or html
    urls = []
    pattern = r'(<img[^>]+(?:data-src|data-srcset|srcset|src)=["\']([^"\']+)["\'])|(<a[^>]+href=["\']([^"\']+)["\'])'
    for match in re.finditer(pattern, source_html, flags=re.I):
        src = match.group(2) or match.group(4)
        if not src:
            continue
        src = src.strip()
        if src.startswith('data:'):
            continue
        if '://' not in src:
            src = urljoin(base_url, src)
        urls.append(src)

    normalized = []
    for src in urls:
        if ',' in src and 'srcset' in src:
            parts = [part.strip().split(' ')[0] for part in src.split(',') if part.strip()]
        else:
            parts = [src]
        for part in parts:
            path = urlparse(part).path
            ext = os.path.splitext(path)[1].lower()
            if ext not in ('.jpg', '.jpeg', '.png', '.webp', '.gif'):
                continue
            if part not in normalized:
                normalized.append(part)

    return normalized


def _extract_price(html):
    if value := _extract_meta(html, 'og:price:amount'):
        return value
    if value := _extract_meta(html, 'price'):
        return value
    match = re.search(r'R\$\s*([0-9\.,]+)', html)
    if match:
        return match.group(1).strip()
    return None


def _extract_address(html):
    for marker in ('Bairro', 'Endereço', 'Endereço:'):
        pattern = rf'{marker}[^<\n]*<[^>]*>([^<]+)</'
        match = re.search(pattern, html, flags=re.I)
        if match:
            return _clean_text(match.group(1))
    return None


def parse_imovel_link(url):
    try:
        html = _download_url(url)
    except (HTTPError, URLError, ValueError):
        return {}

    titulo = (
        _extract_meta(html, 'og:title')
        or _extract_meta(html, 'twitter:title')
        or _extract_tag_text(html, 'h1')
        or _extract_tag_text(html, 'title')
    )
    descricao = (
        _extract_meta(html, 'og:description')
        or _extract_meta(html, 'twitter:description')
        or _extract_tag_text(html, 'p')
    )
    valor = _extract_price(html)
    endereco = _extract_address(html)
    imagens = _extract_image_urls(html, url)

    return {
        'titulo': titulo,
        'descricao': descricao,
        'valor': valor,
        'endereco': endereco,
        'image_urls': imagens,
    }


def download_remote_image(url, timeout=20):
    try:
        request = Request(url, headers={'User-Agent': USER_AGENT})
        with urlopen(request, timeout=timeout) as response:
            return response.read(), urlparse(url).path.split('/')[-1] or 'imagem.jpg'
    except (HTTPError, URLError, ValueError):
        return None, None
