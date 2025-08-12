# 📚 Documentação Técnica: Integração IA

## 🏗️ Arquitetura da Solução

### Visão Geral
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Frontend     │───▶│     Backend     │───▶│      n8n        │
│   (React/JS)    │    │    (Flask)      │    │   (Workflow)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │     Redis       │    │   Gemini Pro    │
                       │    (Cache)      │    │     (IA)        │
                       └─────────────────┘    └─────────────────┘
```

### Fluxo de Dados
1. **Frontend** → Envia URL para análise
2. **Backend** → Processa dados básicos + chama n8n
3. **n8n** → Executa workflow com Gemini Pro
4. **Gemini Pro** → Retorna análise avançada
5. **Backend** → Combina resultados + cache
6. **Frontend** → Exibe resultados enriquecidos

## 🔧 Componentes Técnicos

### 1. Backend Flask (`ai_analysis.py`)

#### Classe Principal: `AIAnalysisEngine`
```python
class AIAnalysisEngine:
    def __init__(self):
        self.n8n_webhook_url = os.getenv('N8N_WEBHOOK_URL')
        self.webhook_secret = os.getenv('N8N_WEBHOOK_SECRET')
        self.timeout = 120  # 2 minutos
```

#### Métodos Principais:

**`perform_analysis(website_data, google_data)`**
- **Input**: Dados do website e Google
- **Output**: Análise completa com IA
- **Timeout**: 120 segundos
- **Fallback**: Análise básica em caso de erro

**`_prepare_analysis_data(website_data, google_data)`**
- Extrai dados técnicos (meta tags, estrutura, performance)
- Detecta tipo de negócio automaticamente
- Formata dados para o Gemini Pro

**`_detect_business_type(website_data)`**
- Análise de conteúdo para detectar setor
- Palavras-chave específicas por categoria
- Fallback para "Geral" se não detectado

### 2. Workflow n8n

#### Estrutura do Workflow
```json
{
  "nodes": [
    {
      "name": "Webhook Trigger",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "website-analysis",
        "httpMethod": "POST"
      }
    },
    {
      "name": "Data Preparation",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "// Prepara dados para Gemini"
      }
    },
    {
      "name": "Gemini SEO Analysis",
      "type": "n8n-nodes-base.googleGemini",
      "parameters": {
        "prompt": "Analise SEO do website..."
      }
    },
    {
      "name": "Gemini Marketing Strategy",
      "type": "n8n-nodes-base.googleGemini",
      "parameters": {
        "prompt": "Crie estratégia de marketing..."
      }
    },
    {
      "name": "Combine Results",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "// Combina resultados das análises"
      }
    },
    {
      "name": "Webhook Response",
      "type": "n8n-nodes-base.respondToWebhook"
    }
  ]
}
```

#### Prompts Otimizados

**SEO Analysis Prompt:**
```
Analise o website com foco em SEO:

Dados do Website:
- URL: {{$json.website_url}}
- Título: {{$json.technical_data.title}}
- Meta Description: {{$json.technical_data.meta_description}}
- Estrutura H1-H6: {{$json.technical_data.headings}}
- Performance: {{$json.technical_data.performance}}

Retorne em JSON:
{
  "score_seo": number (0-100),
  "priority_actions": ["ação1", "ação2", "ação3"],
  "technical_issues": ["problema1", "problema2"],
  "content_recommendations": ["rec1", "rec2"],
  "estimated_impact": {
    "traffic_increase": "percentage",
    "ranking_improvement": "description"
  }
}
```

**Marketing Strategy Prompt:**
```
Crie estratégia de marketing digital:

Contexto:
- Tipo de Negócio: {{$json.business_type}}
- Conteúdo Principal: {{$json.content_data.main_content}}
- Concorrentes: {{$json.google_data.competitors}}
- Presença Digital: {{$json.google_data.social_presence}}

Retorne em JSON:
{
  "recommended_channels": ["canal1", "canal2"],
  "content_strategy": {
    "blog_topics": ["tópico1", "tópico2"],
    "social_media": ["estratégia1", "estratégia2"]
  },
  "paid_advertising": {
    "google_ads_keywords": ["palavra1", "palavra2"],
    "facebook_audiences": ["audiência1", "audiência2"]
  },
  "budget_allocation": {
    "seo": "percentage",
    "paid_ads": "percentage",
    "content": "percentage",
    "social_media": "percentage"
  }
}
```

### 3. Sistema de Cache (Redis)

#### Configuração
```python
import redis
from datetime import timedelta

redis_client = redis.from_url(
    os.getenv('REDIS_URL', 'redis://localhost:6379'),
    decode_responses=True
)

CACHE_TTL = int(os.getenv('CACHE_TTL', 3600))  # 1 hora
```

#### Estratégia de Cache
- **Chave**: `analysis:{hash(website_url)}`
- **TTL**: 1 hora (configurável)
- **Dados**: Análise completa em JSON
- **Invalidação**: Manual ou por TTL

#### Implementação
```python
def get_cached_analysis(website_url):
    cache_key = f"analysis:{hashlib.md5(website_url.encode()).hexdigest()}"
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        return json.loads(cached_data)
    return None

def cache_analysis(website_url, analysis_data):
    cache_key = f"analysis:{hashlib.md5(website_url.encode()).hexdigest()}"
    redis_client.setex(
        cache_key, 
        CACHE_TTL, 
        json.dumps(analysis_data)
    )
```

### 4. Frontend Integration

#### Estado da Aplicação
```javascript
const appState = {
    aiAvailable: false,
    analysisInProgress: false,
    currentAnalysis: null,
    analysisHistory: []
};
```

#### Funções Principais

**`checkAIAvailability()`**
```javascript
async function checkAIAvailability() {
    try {
        const response = await fetch('/ai-status');
        const data = await response.json();
        
        appState.aiAvailable = data.ai_available;
        updateUIBasedOnAIStatus(data);
    } catch (error) {
        console.log('IA não disponível:', error);
        appState.aiAvailable = false;
    }
}
```

**`analisarComIA()`**
```javascript
async function analisarComIA() {
    const websiteUrl = getWebsiteUrl();
    
    if (!websiteUrl) {
        showError('URL inválida');
        return;
    }
    
    showAILoading(true);
    appState.analysisInProgress = true;
    
    try {
        const response = await fetch('/analisar-ia', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ website_url: websiteUrl })
        });
        
        const data = await response.json();
        
        if (data.ai_analysis?.success) {
            displayAIResults(data);
            appState.currentAnalysis = data;
        } else {
            displayBasicResults(data.basic_analysis);
        }
    } catch (error) {
        handleAnalysisError(error);
    } finally {
        showAILoading(false);
        appState.analysisInProgress = false;
    }
}
```

## 🔒 Segurança

### Autenticação e Autorização

#### n8n Security
```yaml
# docker-compose-with-n8n.yml
n8n:
  environment:
    - N8N_BASIC_AUTH_ACTIVE=true
    - N8N_BASIC_AUTH_USER=${N8N_AUTH_USER}
    - N8N_BASIC_AUTH_PASSWORD=${N8N_AUTH_PASSWORD}
    - N8N_WEBHOOK_TUNNEL_URL=http://localhost:5678
```

#### Webhook Security
```python
def verify_webhook_signature(request_data, signature):
    expected_signature = hmac.new(
        webhook_secret.encode(),
        request_data.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)
```

#### API Key Protection
```python
# Nunca expor API keys no frontend
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY não configurada")
```

### Rate Limiting
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@app.route('/analisar-ia', methods=['POST'])
@limiter.limit("10 per minute")
def analisar_ia():
    # Implementação da análise
    pass
```

## 📊 Monitoramento e Logs

### Estrutura de Logs
```python
import logging
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_analysis.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('ai_analysis')

# Logs estruturados
def log_analysis_start(website_url, analysis_type):
    logger.info(f"Analysis started", extra={
        'website_url': website_url,
        'analysis_type': analysis_type,
        'timestamp': datetime.utcnow().isoformat()
    })

def log_analysis_complete(website_url, duration, success):
    logger.info(f"Analysis completed", extra={
        'website_url': website_url,
        'duration_seconds': duration,
        'success': success,
        'timestamp': datetime.utcnow().isoformat()
    })
```

### Métricas de Performance
```python
import time
from functools import wraps

def measure_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            success = True
        except Exception as e:
            result = None
            success = False
            raise
        finally:
            duration = time.time() - start_time
            log_performance_metric(func.__name__, duration, success)
        return result
    return wrapper

@measure_performance
def perform_ai_analysis(website_data, google_data):
    # Implementação da análise
    pass
```

### Health Checks
```python
@app.route('/health')
def health_check():
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {
            'redis': check_redis_health(),
            'n8n': check_n8n_health(),
            'gemini': check_gemini_health()
        }
    }
    
    overall_healthy = all(health_status['services'].values())
    health_status['status'] = 'healthy' if overall_healthy else 'unhealthy'
    
    status_code = 200 if overall_healthy else 503
    return jsonify(health_status), status_code
```

## 🚀 Performance e Otimização

### Otimizações de Performance

#### 1. Processamento Assíncrono
```python
import asyncio
import aiohttp

async def perform_parallel_analysis(website_data, google_data):
    tasks = [
        analyze_seo_async(website_data),
        analyze_marketing_async(google_data),
        analyze_technical_async(website_data)
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return combine_analysis_results(results)
```

#### 2. Cache Inteligente
```python
def get_cache_key(website_url, analysis_type='full'):
    # Incluir hash do conteúdo para invalidação automática
    content_hash = get_website_content_hash(website_url)
    return f"analysis:{analysis_type}:{content_hash}"

def should_refresh_cache(website_url):
    last_analysis = get_last_analysis_time(website_url)
    if not last_analysis:
        return True
    
    # Refresh se passou mais de 6 horas
    return (datetime.utcnow() - last_analysis).seconds > 21600
```

#### 3. Batch Processing
```python
def analyze_multiple_websites(website_urls):
    batch_size = 5
    results = []
    
    for i in range(0, len(website_urls), batch_size):
        batch = website_urls[i:i + batch_size]
        batch_results = process_website_batch(batch)
        results.extend(batch_results)
        
        # Rate limiting entre batches
        time.sleep(2)
    
    return results
```

### Otimizações de Custo

#### 1. Prompt Engineering
```python
# Prompts otimizados para reduzir tokens
SEO_PROMPT_OPTIMIZED = """
Analise SEO (resposta JSON apenas):
URL: {url}
Título: {title}
Meta: {meta}

Retorne:
{"score": 0-100, "actions": ["top 3"], "impact": "estimativa"}
"""

# Vs prompt verboso que custa mais
SEO_PROMPT_VERBOSE = """
Por favor, analise detalhadamente o SEO do website...
[muito texto desnecessário]
"""
```

#### 2. Cache Estratégico
```python
# Cache por tipo de análise
CACHE_STRATEGIES = {
    'seo_basic': 3600,      # 1 hora
    'seo_detailed': 7200,   # 2 horas
    'marketing': 14400,     # 4 horas
    'competitive': 86400    # 24 horas
}
```

## 🧪 Testes

### Testes Unitários
```python
import unittest
from unittest.mock import patch, MagicMock

class TestAIAnalysisEngine(unittest.TestCase):
    def setUp(self):
        self.engine = AIAnalysisEngine()
        self.sample_website_data = {
            'url': 'https://example.com',
            'title': 'Example Site',
            'meta_description': 'Example description'
        }
    
    @patch('ai_analysis.requests.post')
    def test_successful_analysis(self, mock_post):
        # Mock da resposta do n8n
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'success': True,
            'seo_analysis': {'score': 85}
        }
        mock_post.return_value = mock_response
        
        result = self.engine.perform_analysis(
            self.sample_website_data, {}
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['seo_analysis']['score'], 85)
    
    def test_business_type_detection(self):
        ecommerce_data = {
            'content': 'comprar produto carrinho checkout'
        }
        
        business_type = self.engine._detect_business_type(ecommerce_data)
        self.assertEqual(business_type, 'E-commerce')
```

### Testes de Integração
```python
class TestN8nIntegration(unittest.TestCase):
    def test_n8n_webhook_connectivity(self):
        response = requests.get(f"{N8N_BASE_URL}/healthz")
        self.assertEqual(response.status_code, 200)
    
    def test_gemini_api_connectivity(self):
        # Teste básico da API Gemini
        test_prompt = "Teste de conectividade"
        result = call_gemini_api(test_prompt)
        self.assertIsNotNone(result)
```

### Testes de Performance
```python
import time

class TestPerformance(unittest.TestCase):
    def test_analysis_performance(self):
        start_time = time.time()
        
        result = perform_ai_analysis(
            self.sample_website_data, {}
        )
        
        duration = time.time() - start_time
        
        # Análise deve completar em menos de 2 minutos
        self.assertLess(duration, 120)
        self.assertTrue(result['success'])
```

## 📈 Roadmap Técnico

### Fase 1: Estabilização (Semanas 1-2)
- [ ] Implementação completa da integração
- [ ] Testes de carga e estabilidade
- [ ] Monitoramento e alertas
- [ ] Documentação completa

### Fase 2: Otimização (Semanas 3-4)
- [ ] Cache inteligente
- [ ] Processamento assíncrono
- [ ] Otimização de prompts
- [ ] Redução de custos

### Fase 3: Expansão (Semanas 5-8)
- [ ] Análise comparativa
- [ ] Relatórios avançados
- [ ] API pública
- [ ] Integração com CRM

### Fase 4: IA Avançada (Semanas 9-12)
- [ ] Modelos customizados
- [ ] Análise preditiva
- [ ] Recomendações automáticas
- [ ] Machine Learning pipeline

---

## 📞 Suporte Técnico

### Contatos
- **Desenvolvedor Principal**: [Seu Nome]
- **Documentação**: Este arquivo + GUIA_IMPLEMENTACAO_IA.md
- **Issues**: GitHub Issues
- **Logs**: `docker-compose logs` ou arquivos de log

### Recursos Úteis
- [Documentação n8n](https://docs.n8n.io/)
- [Gemini Pro API](https://ai.google.dev/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Redis Documentation](https://redis.io/documentation)

**Última atualização**: Janeiro 2024
**Versão**: 1.0.0