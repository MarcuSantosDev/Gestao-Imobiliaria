# ImobiGest CRM

Sistema web para gestão imobiliária: imóveis, clientes, corretores, demandas e relatórios.

## Requisitos

- Python 3.13+
- Django 5+

## Instalação

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_dados
```

## Executar localmente

```bash
python manage.py runserver
```

Acesse: http://127.0.0.1:8000/

## Módulos

- **Dashboard** — indicadores gerais do negócio
- **Imóveis** — cadastro, fotos, infraestrutura e compartilhamento WhatsApp
- **Clientes** — cadastro e busca de clientes
- **Corretores** — autônomos e imobiliárias
- **Demandas** — captação de necessidades e busca inteligente
- **Relatórios** — imóveis, corretores e demandas

## Admin Django

```bash
python manage.py createsuperuser
```

Acesse: http://127.0.0.1:8000/admin/
