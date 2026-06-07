# Gestão Imobiliária

Sistema CRM imobiliário desenvolvido em Django para gestão de imóveis, clientes, corretores e demandas.

## Principais recursos

- Cadastro de imóveis, clientes e corretores
- Busca inteligente de imóveis por compatibilidade com demandas
- Dashboard com indicadores e atalhos
- Upload múltiplo de fotos com recorte
- Compartilhamento de imóveis via WhatsApp
- Download de fotos em ZIP
- Histórico de imóveis e demandas finalizadas
- Exclusão automática de arquivos de imagem ao remover fotos ou imóveis

## Requisitos

- Python 3.13+
- pip

## Instalação

```bash
git clone <url-do-repositorio>
cd Gestao-Imobiliaria

python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt

python manage.py migrate
python manage.py seed_dados
python manage.py runserver
```

Acesse:

```text
http://127.0.0.1:8000/
```

### Windows (atalho)

Após criar a venv e instalar as dependências, execute:

```text
iniciar.bat
```

## Dados de teste (opcional)

```bash
python manage.py populate_db
```

Cria dados fictícios para demonstração do sistema.

```bash
python manage.py populate_db --clear
```

Remove os dados de teste gerados.

## Módulos

| Módulo     | Função                                      |
| ---------- | ------------------------------------------- |
| Dashboard  | Visão geral do sistema                      |
| Imóveis    | Cadastro, fotos, filtros e compartilhamento |
| Clientes   | Cadastro e gerenciamento de clientes        |
| Corretores | Cadastro de corretores e imobiliárias       |
| Demandas   | Busca inteligente de imóveis                |
| Histórico  | Imóveis e demandas finalizadas              |

## Comandos úteis

```bash
python manage.py runserver
python manage.py migrate
python manage.py seed_dados
python manage.py createsuperuser
python manage.py check
```

## Admin Django

```bash
python manage.py createsuperuser
```

Acesse:

```text
http://127.0.0.1:8000/admin/
```

## Estrutura do projeto

```text
Gestao-Imobiliaria/
├── apps/
├── project/
├── templates/
├── static/
├── media/
├── manage.py
├── requirements.txt
└── iniciar.bat
```

## Tecnologias

- Django
- Pillow
- django-filter
- Bootstrap 5
- Cropper.js
- SQLite

## Observações

- `seed_dados` cadastra as infraestruturas iniciais do sistema.
- Arquivos enviados pelos usuários são armazenados em `media/`.
- Ao excluir uma foto ou imóvel, os arquivos associados são removidos automaticamente.
- Projeto configurado para desenvolvimento local utilizando SQLite.

## Licença

Este projeto é proprietário. Todos os direitos são reservados a Marcus Vinicius Vieira Santos. Consulte o arquivo LICENSE para mais informações.
