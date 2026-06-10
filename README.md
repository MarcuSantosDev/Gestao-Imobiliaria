🏢 Gestão Imobiliária


![Status](https://img.shields.io/badge/status-production-brightgreen)
![Architecture](https://img.shields.io/badge/architecture-saas-orange)

Sistema CRM imobiliário desenvolvido em Django para gestão de imóveis, clientes, corretores e demandas.

A aplicação está hospedada na Fly.io, utiliza banco de dados na Neon (PostgreSQL) e armazenamento de imagens na Cloudinary. Conta com sistema de usuários com autenticação, onde cada usuário possui suas próprias demandas e compartilha a base de imóveis da plataforma.

## 🚀 Principais recursos
- Cadastro de imóveis, clientes e corretores
- Sistema de usuários com autenticação
- Cada usuário possui suas próprias demandas
- Base compartilhada de imóveis entre usuários
- Busca inteligente de imóveis por compatibilidade com demandas
- Dashboard com indicadores e atalhos
- Upload múltiplo de fotos com recorte
- Armazenamento de imagens na Cloudinary
- Compartilhamento via WhatsApp
- Download de imagens em ZIP
- Histórico de imóveis e demandas finalizadas
- Exclusão automática de arquivos de mídia
- Deploy em produção na Fly.io
- Banco de dados PostgreSQL na Neon

## ☁️ Arquitetura SaaS
- Camada	Serviço
- Hosting	Fly.io
- Database	Neon (PostgreSQL)
- Storage	Cloudinary
- Container	Docker
- 
## 🧠 Banco de dados
- 🧪 Local: SQLite (db.sqlite3)
- 🌍 Produção: PostgreSQL (Neon via DATABASE_URL)

O sistema alterna automaticamente entre ambientes com base no DEBUG.

## 🐳 Docker
📦 Build da imagem
docker build -t gestao-imobiliaria .
▶️ Rodar container
docker run -p 8000:8000 gestao-imobiliaria

## 🌐 Acessar
http://localhost:8000/ ou http://127.0.0.1:8000/

## ⚙️ Instalação local
1. Clonar o projeto
git clone https://github.com/MarcuSantosDev/Gestao-Imobiliaria.git
cd Gestao-Imobiliaria
2. Criar ambiente virtual
python -m venv venv
3. Ativar ambiente

Windows

.\venv\Scripts\Activate.ps1

Linux/macOS

source venv/bin/activate
4. Instalar dependências
pip install -r requirements.txt
5. Migrar banco
python manage.py migrate
6. Rodar servidor
python manage.py runserver

## 📊 Módulos
- Módulo	Função
- Dashboard	Visão geral do sistema
- Imóveis	Cadastro e gestão
- Clientes	CRM de clientes
- Corretores	Gestão de parceiros
- Demandas	Matching inteligente
- Usuários	Autenticação e isolamento
- Histórico	Registros finalizados
- 
## 🧰 Tecnologias
- Django
- PostgreSQL (Neon)
- Cloudinary
- Fly.io
- Docker
- Bootstrap 5
- Pillow
- django-filter
- Cropper.js
- 
## ⚡ Deploy
- Deploy contínuo via Fly.io
- Variáveis de ambiente via .env
- Storage externo via Cloudinary
- Banco gerenciado via Neon
- 
## 🧪 Observações
- SQLite usado apenas em desenvolvimento
- Produção isolada via PostgreSQL
- Uploads em Cloudinary
- Projeto pronto para SaaS escalável
- Arquitetura preparada para multi-usuário
- 
## 📜 Licença
Este projeto é proprietário. Todos os direitos são reservados a Marcus Vinicius Vieira Santos. Consulte o arquivo LICENSE para mais informações.
