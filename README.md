# Gestão Imobiliária - CRM

Sistema web para gestão imobiliária desenvolvido com Django. Permite cadastrar imóveis, clientes e corretores, gerenciar demandas de clientes com busca inteligente de compatibilidade, acompanhar indicadores no dashboard e consultar o histórico de negócios concluídos.

## Requisitos

- [Python](https://www.python.org/downloads/) 3.13 ou superior
- `pip` (geralmente já vem com o Python)

## Como rodar o projeto

### 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd Gestao-Imobiliaria
```

### 2. Criar e ativar o ambiente virtual

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4. Aplicar as migrações do banco de dados

```bash
python manage.py migrate
```

O projeto usa **SQLite** por padrão. O arquivo `db.sqlite3` será criado automaticamente na raiz do projeto.

### 5. (Opcional) Popular dados iniciais

Para cadastrar categorias e infraestruturas usadas nos formulários:

```bash
python manage.py seed_dados
```

Para popular o banco com dados de teste (clientes, corretores, 50 imóveis e demandas):

```bash
python manage.py populate_db --clear
```

> Use `--clear` para apagar os dados de teste anteriores antes de popular novamente.  
> Para alterar a quantidade de imóveis: `python manage.py populate_db --clear --imoveis 50`

### 6. Iniciar o servidor

```bash
python manage.py runserver
```

Acesse no navegador: **http://127.0.0.1:8000/**

## Comandos úteis

| Comando | Descrição |
|---------|-----------|
| `python manage.py runserver` | Sobe o servidor de desenvolvimento |
| `python manage.py migrate` | Aplica migrações do banco |
| `python manage.py seed_dados` | Cadastra categorias e infraestruturas |
| `python manage.py populate_db --clear` | Popula o banco com dados de teste |
| `python manage.py createsuperuser` | Cria usuário para o painel admin |
| `python manage.py check` | Verifica se o projeto está configurado corretamente |

## Módulos do sistema

| Módulo | Rota | Descrição |
|--------|------|-----------|
| Dashboard | `/` | Indicadores gerais e atalhos |
| Imóveis | `/imoveis/` | Cadastro, fotos, filtros e compartilhamento WhatsApp |
| Clientes | `/clientes/` | Cadastro e gestão de clientes |
| Corretores | `/corretores/` | Autônomos e imobiliárias |
| Demandas | `/demandas/` | Demandas abertas e busca inteligente de imóveis |
| Histórico | `/historico/` | Demandas finalizadas e imóveis vendidos, alugados ou reservados |

## Painel administrativo (opcional)

Para acessar o admin do Django:

```bash
python manage.py createsuperuser
```

Depois acesse: **http://127.0.0.1:8000/admin/**

## Estrutura do projeto

```
Gestao-Imobiliaria/
├── apps/
│   ├── dashboard/      # Página inicial e indicadores
│   ├── clientes/       # Módulo de clientes
│   ├── corretores/     # Módulo de corretores
│   ├── imoveis/        # Imóveis, modelos principais e comandos de seed
│   ├── demandas/       # Demandas e busca inteligente
│   └── relatorios/     # Histórico (demandas e imóveis concluídos)
├── project/            # Configurações Django (settings, urls)
├── templates/        # Templates globais
├── static/             # Arquivos estáticos (JS, CSS)
├── media/              # Uploads (fotos de imóveis)
├── manage.py
└── requirements.txt
```

## Tecnologias

- Django 6
- Bootstrap 5
- SQLite
- Pillow (upload de imagens)

## Observações

- O idioma padrão do sistema é **pt-BR** e o fuso horário é **America/Sao_Paulo**.
- As fotos dos imóveis são salvas na pasta `media/`.
- Este projeto é voltado para **desenvolvimento local**. Para produção, configure variáveis de ambiente, `SECRET_KEY`, `DEBUG = False` e um banco de dados adequado.
