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

### 1. Clonar o repositório

```bash
git clone https://github.com/MarcuSantosDev/Gestao-Imobiliaria.git
cd Gestao-Imobiliaria
```

### 2. Criar o ambiente virtual

```bash
python -m venv venv
```

### 3. Ativar o ambiente virtual

**Windows**

```powershell
.\venv\Scripts\Activate.ps1
```

**Linux / macOS**

```bash
source venv/bin/activate
```

### 4. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 5. Aplicar as migrações

```bash
python manage.py migrate
```

### 6. Cadastrar os dados iniciais

```bash
python manage.py seed_dados
```

### 7. Iniciar o servidor

```bash
python manage.py runserver
```

### 8. Acessar o sistema

```text
http://127.0.0.1:8000/
```

### Windows (atalho)

Após concluir a instalação uma vez, você pode iniciar o projeto apenas executando:

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

- O banco de dados (`db.sqlite3`) não faz parte do repositório.
- Execute `python manage.py migrate` para criar a estrutura do banco local.
- `seed_dados` cadastra as infraestruturas iniciais do sistema.
- Arquivos enviados pelos usuários são armazenados em `media/`.
- Ao excluir uma foto ou imóvel, os arquivos associados são removidos automaticamente.
- Projeto configurado para desenvolvimento local utilizando SQLite.

## Licença

Este projeto é proprietário. Todos os direitos são reservados a Marcus Vinicius Vieira Santos. Consulte o arquivo LICENSE para mais informações.
