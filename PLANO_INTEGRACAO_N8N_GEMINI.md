# 🚀 Plano de Integração: n8n + Gemini Pro

## 📋 Visão Geral
Integração do n8n com Gemini Pro para análises mais avançadas e certeiras, mantendo compatibilidade com o frontend atual.

## 🏗️ Arquitetura Proposta

### 1. Fluxo Atual vs. Novo Fluxo

**Fluxo Atual:**
```
Frontend → Backend Flask → Análise Básica → Resposta JSON
```

**Novo Fluxo com IA:**
```
Frontend → Backend Flask → n8n Workflow → Gemini Pro → Análise Avançada → Backend → Resposta JSON
```

### 2. Componentes da Integração

#### A. n8n Workflow
- **Trigger**: HTTP Request do Backend Flask
- **Processamento**: Preparação dos dados coletados
- **IA**: Chamada para Gemini Pro com prompts especializados
- **Resposta**: Retorno estruturado para o Backend

#### B. Gemini Pro Integration
- **Análise de Website**: Prompts específicos para SEO, UX, Performance
- **Análise de Presença Digital**: Avaliação de estratégias de marketing
- **Recomendações Personalizadas**: Sugestões baseadas no nicho/setor

## 🔧 Implementação Técnica

### 1. Configuração do n8n

#### Docker Compose Atualizado
```yaml
version: '3.8'
services:
  # Serviços existentes...
  
  n8n:
    image: n8nio/n8n:latest
    container_name: n8n_analysis
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=admin123
      - WEBHOOK_URL=http://localhost:5678
    volumes:
      - n8n_data:/home/node/.n8n
    networks:
      - app-network

volumes:
  n8n_data:

networks:
  app-network:
    driver: bridge
```

### 2. Backend Flask - Nova Rota

#### Nova Rota: `/analisar-ia`
```python
@app.route('/analisar-ia', methods=['POST', 'OPTIONS'])
def analisar_com_ia():
    """Análise avançada usando n8n + Gemini Pro"""
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        data = request.json
        website_url = data.get('website_url', '').strip()
        
        if not website_url:
            return jsonify({'error': 'URL do website deve ser fornecido'}), 400
        
        # 1. Coleta dados básicos (código existente)
        basic_analysis = perform_basic_analysis(website_url)
        
        # 2. Envia para n8n para análise com IA
        ai_analysis = send_to_n8n_workflow(basic_analysis, website_url)
        
        # 3. Combina resultados
        result = {
            'timestamp': datetime.now().isoformat(),
            'website_url': website_url,
            'basic_analysis': basic_analysis,
            'ai_analysis': ai_analysis,
            'enhanced_recommendations': ai_analysis.get('recommendations', [])
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro na análise: {str(e)}'}), 500
```

### 3. Função de Integração com n8n

```python
import requests

def send_to_n8n_workflow(basic_data, website_url):
    """Envia dados para workflow n8n com Gemini Pro"""
    n8n_webhook_url = "http://n8n:5678/webhook/analyze-website"
    
    payload = {
        'website_url': website_url,
        'basic_analysis': basic_data,
        'analysis_type': 'comprehensive',
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        response = requests.post(
            n8n_webhook_url,
            json=payload,
            timeout=60  # 60 segundos para análise IA
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {'error': 'Falha na análise IA', 'fallback': True}
            
    except Exception as e:
        print(f"Erro ao conectar com n8n: {e}")
        return {'error': str(e), 'fallback': True}
```

### 4. n8n Workflow Structure

#### Nodes do Workflow:
1. **Webhook Trigger** - Recebe dados do Backend
2. **Data Preparation** - Formata dados para Gemini
3. **Gemini Pro Node** - Análise com IA
4. **Response Formatter** - Estrutura resposta
5. **HTTP Response** - Retorna para Backend

#### Prompts para Gemini Pro:

**Prompt de Análise SEO:**
```
Analise os seguintes dados de website e forneça recomendações específicas de SEO:

URL: {{website_url}}
Dados técnicos: {{technical_data}}
Conteúdo: {{content_analysis}}

Forneça:
1. Análise técnica detalhada
2. Oportunidades de palavras-chave
3. Melhorias de conteúdo
4. Estratégias de link building
5. Priorização de ações (1-3 meses)

Formato: JSON estruturado
```

**Prompt de Estratégia Digital:**
```
Com base na análise do website, crie uma estratégia de marketing digital:

Setor: {{business_sector}}
Concorrência: {{competitor_analysis}}
Presença atual: {{current_presence}}

Forneça:
1. Estratégia de conteúdo
2. Campanhas Google Ads sugeridas
3. Presença em redes sociais
4. Métricas de acompanhamento
5. Budget estimado

Formato: JSON com prioridades
```

### 5. Frontend - Integração

#### Botão de Análise Avançada
```javascript
// Adicionar ao index.html
function analisarComIA() {
    const websiteUrl = document.getElementById('website-url').value;
    
    if (!websiteUrl) {
        alert('Por favor, insira uma URL válida');
        return;
    }
    
    // Mostrar loading específico para IA
    showAIAnalysisLoading();
    
    fetch('/analisar-ia', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ website_url: websiteUrl })
    })
    .then(response => response.json())
    .then(data => {
        hideAIAnalysisLoading();
        displayAIAnalysis(data);
    })
    .catch(error => {
        hideAIAnalysisLoading();
        console.error('Erro na análise IA:', error);
    });
}

function displayAIAnalysis(data) {
    // Exibir resultados da análise IA
    const aiSection = document.getElementById('ai-analysis-results');
    
    if (data.ai_analysis && !data.ai_analysis.fallback) {
        // Mostrar análise IA avançada
        aiSection.innerHTML = formatAIAnalysis(data.ai_analysis);
    } else {
        // Fallback para análise básica
        aiSection.innerHTML = formatBasicAnalysis(data.basic_analysis);
    }
}
```

## 📊 Benefícios da Integração

### 1. Análises Mais Precisas
- **IA Contextual**: Gemini Pro entende contexto do negócio
- **Recomendações Personalizadas**: Baseadas no setor/nicho
- **Análise Competitiva**: Comparação com concorrentes

### 2. Escalabilidade
- **Workflows Modulares**: Fácil adição de novas análises
- **Processamento Assíncrono**: Não bloqueia interface
- **Cache Inteligente**: Evita reprocessamento desnecessário

### 3. Manutenibilidade
- **Separação de Responsabilidades**: IA isolada em workflows
- **Fallback Automático**: Análise básica se IA falhar
- **Logs Detalhados**: Monitoramento de performance

## 🚀 Roadmap de Implementação

### Fase 1: Setup Básico (1-2 dias)
- [ ] Configurar n8n no Docker Compose
- [ ] Criar workflow básico
- [ ] Integrar Gemini Pro API
- [ ] Testar comunicação Backend ↔ n8n

### Fase 2: Análises IA (3-4 dias)
- [ ] Desenvolver prompts especializados
- [ ] Implementar rota `/analisar-ia`
- [ ] Criar sistema de fallback
- [ ] Testes de integração

### Fase 3: Frontend (1-2 dias)
- [ ] Adicionar botão "Análise IA"
- [ ] Implementar loading states
- [ ] Criar interface para resultados IA
- [ ] Testes de usabilidade

### Fase 4: Otimização (2-3 dias)
- [ ] Implementar cache
- [ ] Otimizar prompts
- [ ] Monitoramento e logs
- [ ] Documentação

## 💰 Considerações de Custo

### APIs Utilizadas
- **Gemini Pro**: ~$0.001 por 1K tokens
- **n8n**: Gratuito (self-hosted)
- **Estimativa**: ~$0.05-0.10 por análise completa

### Otimizações de Custo
- Cache de resultados (24h)
- Prompts otimizados (menos tokens)
- Análise incremental
- Rate limiting

## 🔒 Segurança

### Variáveis de Ambiente
```env
# Adicionar ao .env
GEMINI_API_KEY=your_gemini_api_key
N8N_WEBHOOK_SECRET=your_webhook_secret
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=secure_password
```

### Validações
- Autenticação n8n
- Rate limiting
- Validação de entrada
- Sanitização de dados

---

**Próximos Passos:**
1. Revisar e aprovar arquitetura
2. Configurar ambiente de desenvolvimento
3. Implementar Fase 1
4. Testes e validação
5. Deploy em produção

Esta integração manterá total compatibilidade com o sistema atual, adicionando uma camada de inteligência artificial para análises mais precisas e recomendações personalizadas.