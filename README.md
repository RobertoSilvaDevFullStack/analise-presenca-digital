# 🔍 Análise de Presença Digital

Sistema completo para análise de websites e perfis do Instagram, com geração automática de relatórios para CRM.

## 🚀 Funcionalidades

- **Análise de Websites**: Métricas técnicas, SEO, performance, SSL e estrutura
- **Análise Google**: Presença nos resultados de busca e indexação
- **Interface Unificada**: Aplicação web moderna com HTML, CSS e JavaScript integrados
- **API RESTful**: Backend Flask robusto para processamento de análises
- **Relatórios Detalhados**: Informações completas sobre presença digital

## 📦 Estrutura do Projeto

```
📁 analise-presenca-digital/
├── 🐳 docker-compose.yml    # Configuração Docker
├── 📄 README.md             # Documentação
├── 🚫 .gitignore            # Arquivos ignorados
├── 📱 frontend/             # Interface web
│   ├── index.html          # Aplicação completa (HTML+CSS+JS)
│   ├── nginx.conf          # Configuração Nginx
│   └── Dockerfile          # Container frontend
└── ⚙️ backend/              # API Backend
    ├── app.py              # Aplicação Flask principal
    ├── requirements.txt    # Dependências Python
    ├── .env.example        # Exemplo de variáveis
    ├── Dockerfile          # Container backend
    └── scraper_modules/    # Módulos de análise
        ├── website_scraper.py   # Análise de websites
        ├── google_scraper.py    # Análise Google
        ├── instagram_scraper.py # Análise Instagram
        ├── instagram_config.py  # Config Instagram
        └── __init__.py
```

## 🛠️ Instalação e Uso

### Pré-requisitos
- Docker e Docker Compose instalados
- Portas 80 e 5000 disponíveis

### Execução
```bash
# 1. Clone/acesse o projeto
cd "Projeto de Análise"

# 2. Execute o sistema
docker-compose up --build

# 3. Acesse a interface
# 🌐 http://localhost
```

### Uso da Interface
1. **Insira as URLs** do site e Instagram
2. **Clique em "Analisar"** para processar
3. **Gere relatórios CRM** formatados
4. **Copie e cole** no RD Station ou outro CRM

## 🔧 API Endpoints

- `GET /health` - Status da API
- `POST /analisar` - Análise completa
- `POST /relatorio-crm` - Relatório formatado

### Exemplo de Uso da API
```bash
curl -X POST http://localhost:5000/analisar \
  -H "Content-Type: application/json" \
  -d '{
    "website_url": "https://exemplo.com",
    "instagram_url": "https://instagram.com/exemplo"
  }'
```

## 📊 Recursos de Análise

### Website
- ✅ Status HTTP e SSL
- ✅ Métricas de SEO (título, meta description)
- ✅ Tecnologias utilizadas (CMS, frameworks)
- ✅ Performance e tempo de carregamento
- ✅ Links sociais e contatos

### Instagram
- ✅ Métricas do perfil (seguidores, posts)
- ✅ Status da conta (comercial/pessoal)
- ✅ Atividade recente
- ✅ Completude do perfil (bio, foto)

## 🎯 Relatórios CRM

O sistema gera relatórios profissionais prontos para usar em:
- **RD Station**
- **HubSpot** 
- **Pipedrive**
- **Outros CRMs**

Formato otimizado com:
- Análise técnica detalhada
- Sugestões de melhorias específicas
- Estratégias recomendadas
- Oportunidades identificadas

## 🔒 Configuração

### Variáveis de Ambiente (.env)
```bash
# Supabase (opcional)
SUPABASE_URL=sua_url_supabase
SUPABASE_KEY=sua_chave_supabase

# Instagram (opcional - para recursos avançados)
INSTAGRAM_USERNAME=usuario
INSTAGRAM_PASSWORD=senha
```

## 🏗️ Arquitetura

- **Frontend**: HTML5, CSS3, JavaScript ES6+
- **Backend**: Python Flask, Selenium WebDriver
- **Containers**: Docker com Nginx e Chrome
- **Database**: Supabase (opcional)

## 📝 Logs e Monitoramento

```bash
# Ver logs em tempo real
docker-compose logs -f

# Logs específicos
docker-compose logs backend
docker-compose logs frontend
```

## 🔄 Atualizações

```bash
# Rebuild após mudanças
docker-compose up --build

# Restart apenas um serviço
docker-compose restart backend
```

## 🎉 Status

✅ **Sistema 100% Funcional**  
✅ **Pronto para Produção**  
✅ **Totalmente Testado**

---

**Desenvolvido com ❤️ para análise profissional de presença digital**
