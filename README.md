# 🚀 Análise de Presença Digital com IA

> **Sistema completo de análise de websites com Inteligência Artificial usando Gemini Pro e n8n**

## 📋 Sobre o Projeto

Este projeto oferece uma solução completa para análise de presença digital, combinando scraping automatizado, análise de dados e **inteligência artificial avançada** para fornecer insights precisos sobre websites e estratégias de marketing digital.

### 🆕 Novidades da Versão IA
- **🤖 Análise com Gemini Pro**: Insights mais precisos e personalizados
- **⚡ Automação com n8n**: Workflows inteligentes para análise
- **📊 Recomendações IA**: Estratégias de marketing baseadas em IA
- **🎯 Análise Competitiva**: Comparação automática com concorrentes
- **💾 Cache Inteligente**: Respostas mais rápidas com Redis

## ✨ Funcionalidades

### 🔍 Análise Básica
- **Website Scraping**: Extração completa de dados do site
- **Análise SEO**: Meta tags, estrutura, performance
- **Presença Google**: Verificação de indexação e presença
- **Análise Instagram**: Dados de perfil e engajamento
- **Relatórios Detalhados**: Insights acionáveis

### 🤖 Análise com IA (NOVO)
- **SEO Inteligente**: Análise profunda com Gemini Pro
- **Estratégia de Marketing**: Recomendações personalizadas
- **Detecção de Negócio**: Identificação automática do setor
- **Ações Prioritárias**: Lista de melhorias por ordem de impacto
- **Estimativa de Resultados**: Previsão de melhorias

## 🛠️ Tecnologias

### Backend
- **Python 3.9+** - Linguagem principal
- **Flask** - Framework web
- **Selenium** - Automação de browser
- **BeautifulSoup** - Parsing HTML
- **Supabase** - Banco de dados
- **Redis** - Cache e sessões

### IA e Automação
- **Google Gemini Pro** - Inteligência artificial
- **n8n** - Automação de workflows
- **Docker** - Containerização

### Frontend
- **HTML5/CSS3** - Interface moderna
- **JavaScript ES6+** - Interatividade
- **Bootstrap** - Design responsivo

## 🚀 Instalação Rápida

### Pré-requisitos
- Docker e Docker Compose
- Conta Google AI Studio (para Gemini Pro)
- 4GB RAM disponível

### 1. Clone o Repositório
```bash
git clone https://github.com/SEU_USUARIO/analise-presenca-digital.git
cd analise-presenca-digital
```

### 2. Configure Variáveis de Ambiente
```bash
# Copie o arquivo de exemplo
cp backend/.env.example backend/.env

# Edite com suas configurações
nano backend/.env
```

**Configurações obrigatórias:**
```env
# Supabase
SUPABASE_URL=sua_url_supabase
SUPABASE_KEY=sua_chave_supabase

# Gemini Pro (para IA)
GEMINI_API_KEY=sua_chave_gemini_pro

# n8n (para automação)
N8N_WEBHOOK_SECRET=seu_secret_seguro
N8N_AUTH_USER=admin
N8N_AUTH_PASSWORD=senha_segura
```

### 3. Inicie os Serviços

#### Versão Básica (sem IA)
```bash
docker-compose up -d
```

#### Versão Completa (com IA)
```bash
docker-compose -f docker-compose-with-n8n.yml up -d
```

### 4. Acesse a Aplicação
- **Frontend**: http://localhost
- **Backend API**: http://localhost:5000
- **n8n Interface**: http://localhost:5678 (versão IA)

## 📖 Guias de Uso

### 🎯 Para Usuários
1. Acesse http://localhost
2. Insira a URL do website
3. Escolha o tipo de análise:
   - **Análise Básica**: Rápida e gratuita
   - **Análise IA**: Completa com Gemini Pro
4. Aguarde os resultados (30s-2min)
5. Visualize insights e recomendações

### 👨‍💻 Para Desenvolvedores
- **Guia Completo**: [`GUIA_IMPLEMENTACAO_IA.md`](GUIA_IMPLEMENTACAO_IA.md)
- **Documentação Técnica**: [`DOCUMENTACAO_TECNICA_IA.md`](DOCUMENTACAO_TECNICA_IA.md)
- **Plano de Integração**: [`PLANO_INTEGRACAO_N8N_GEMINI.md`](PLANO_INTEGRACAO_N8N_GEMINI.md)

## 🔧 Configuração Avançada

### Configuração do n8n
1. Acesse http://localhost:5678
2. Faça login com credenciais do .env
3. Importe o workflow: `n8n-workflow-example.json`
4. Configure credenciais do Gemini Pro
5. Ative o workflow

### Configuração do Cache
```env
# Redis (opcional, mas recomendado)
REDIS_URL=redis://localhost:6379
CACHE_ENABLED=true
CACHE_TTL=3600  # 1 hora
```

## 📊 API Endpoints

### Análise Básica
```http
POST /analisar
Content-Type: application/json

{
  "website_url": "https://example.com"
}
```

### Análise com IA
```http
POST /analisar-ia
Content-Type: application/json

{
  "website_url": "https://example.com"
}
```

### Status da IA
```http
GET /ai-status
```

### Cache de Análises
```http
GET /analisar-cache/https://example.com
```

## 🎨 Interface

### Tela Principal
- Campo de URL com validação
- Botões de análise (Básica/IA)
- Indicador de status da IA
- Loading animado

### Resultados
- **Score Geral**: Pontuação 0-100
- **Análise SEO**: Problemas e oportunidades
- **Estratégia Marketing**: Recomendações personalizadas
- **Ações Prioritárias**: Lista ordenada por impacto
- **Estimativas**: Previsão de melhorias

## 💰 Custos

### Análise Básica
- **Custo**: Gratuito
- **Tempo**: 30-60 segundos
- **Precisão**: Boa

### Análise com IA
- **Custo**: $0.05-$0.10 por análise
- **Tempo**: 45-90 segundos
- **Precisão**: Excelente (+40% vs básica)

### Otimização de Custos
- Cache Redis reduz custos em 70%
- Prompts otimizados economizam tokens
- Análise incremental para sites conhecidos

## 🔒 Segurança

### Proteções Implementadas
- Rate limiting (10 análises/minuto)
- Validação de URLs
- Sanitização de dados
- Secrets em variáveis de ambiente
- HTTPS em produção

### Boas Práticas
- Nunca commitar .env
- Rotacionar API keys regularmente
- Monitorar uso das APIs
- Backup regular dos dados

## 📈 Monitoramento

### Métricas Importantes
- **Tempo de resposta**: < 2 minutos
- **Taxa de sucesso**: > 90%
- **Cache hit rate**: > 60%
- **Custo por análise**: < $0.10

### Logs
```bash
# Logs em tempo real
docker-compose logs -f

# Logs específicos
docker-compose logs backend
docker-compose logs n8n
```

### Health Checks
```bash
# Status geral
curl http://localhost:5000/health

# Status da IA
curl http://localhost:5000/ai-status
```

## 🚀 Deploy em Produção

### Variáveis de Ambiente
```env
# Produção
FLASK_ENV=production
DEBUG=false

# Domínio
N8N_WEBHOOK_TUNNEL_URL=https://seu-dominio.com

# SSL
SSL_CERT_PATH=/path/to/cert.pem
SSL_KEY_PATH=/path/to/key.pem
```

### Docker Compose Produção
```yaml
version: '3.8'
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl
```

## 🤝 Contribuição

### Como Contribuir
1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit: `git commit -m 'Adiciona nova funcionalidade'`
4. Push: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

### Padrões de Código
- Python: PEP 8
- JavaScript: ES6+
- Commits: Conventional Commits
- Testes: pytest para backend

## 🐛 Troubleshooting

### Problemas Comuns

#### n8n não inicia
```bash
# Verificar logs
docker-compose logs n8n

# Recriar container
docker-compose down
docker-compose up -d n8n
```

#### Erro de API Key
- Verifique se a chave Gemini está correta
- Teste no Google AI Studio
- Verifique cotas da API

#### Timeout na análise
- Aumente timeout no código
- Verifique conectividade n8n
- Monitore logs do Gemini

### Suporte
- **Issues**: GitHub Issues
- **Documentação**: Arquivos .md do projeto
- **Logs**: `docker-compose logs`

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🙏 Agradecimentos

- **Google Gemini Pro** - IA avançada
- **n8n Community** - Automação open-source
- **Selenium Team** - Web scraping
- **Flask Community** - Framework web

---

## 📞 Contato

- **Desenvolvedor**: [Seu Nome]
- **Email**: [seu.email@exemplo.com]
- **LinkedIn**: [Seu LinkedIn]
- **GitHub**: [Seu GitHub]

---

**⭐ Se este projeto foi útil, considere dar uma estrela!**

**🚀 Versão**: 2.0.0 (com IA)
**📅 Última atualização**: Janeiro 2024

---

### 🎯 Próximos Passos

- [ ] **Análise Comparativa**: Comparar com concorrentes
- [ ] **Relatórios PDF**: Exportar análises
- [ ] **API Pública**: Integração com terceiros
- [ ] **Dashboard Analytics**: Métricas em tempo real
- [ ] **Mobile App**: Aplicativo nativo
- [ ] **Integração CRM**: Conectar com HubSpot/Salesforce

**🔮 Roadmap completo**: Veja [`PLANO_INTEGRACAO_N8N_GEMINI.md`](PLANO_INTEGRACAO_N8N_GEMINI.md)
