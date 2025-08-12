# 🚀 Guia de Deploy - Análise de Presença Digital

## 📋 Visão Geral

Este projeto pode ser deployado em duas plataformas principais:
- **Vercel** - Para aplicação web completa (Frontend + Backend)
- **Streamlit Cloud** - Para interface simplificada

---

## 🌐 Deploy na Vercel

### 📦 Pré-requisitos
- Conta no GitHub
- Conta na Vercel
- Chave API do Google Gemini

### 🔧 Configuração

1. **Push para GitHub:**
   ```bash
   git add .
   git commit -m "Preparação para deploy Vercel"
   git push origin main
   ```

2. **Conectar na Vercel:**
   - Acesse [vercel.com](https://vercel.com)
   - Importe seu repositório GitHub
   - A Vercel detectará automaticamente o `vercel.json`

3. **Configurar Variáveis de Ambiente:**
   No painel da Vercel, adicione:
   ```
   GEMINI_API_KEY=sua_chave_gemini_aqui
   N8N_WEBHOOK_URL=sua_url_n8n_aqui
   N8N_WEBHOOK_SECRET=seu_secret_aqui
   FLASK_ENV=production
   ```

4. **Deploy:**
   - Clique em "Deploy"
   - Aguarde o build completar
   - Sua aplicação estará disponível em `https://seu-projeto.vercel.app`

### 🔗 URLs da Aplicação
- **Frontend:** `https://seu-projeto.vercel.app`
- **API:** `https://seu-projeto.vercel.app/api/analisar`
- **Status IA:** `https://seu-projeto.vercel.app/api/ai-status`

---

## 📊 Deploy no Streamlit Cloud

### 📦 Pré-requisitos
- Conta no GitHub
- Conta no Streamlit Cloud

### 🔧 Configuração

1. **Push para GitHub:**
   ```bash
   git add .
   git commit -m "Preparação para deploy Streamlit"
   git push origin main
   ```

2. **Deploy no Streamlit:**
   - Acesse [share.streamlit.io](https://share.streamlit.io)
   - Clique em "New app"
   - Conecte seu repositório GitHub
   - Defina:
     - **Main file path:** `streamlit_app.py`
     - **Python version:** 3.9

3. **Configurar Secrets:**
   No painel do Streamlit, adicione em "Secrets":
   ```toml
   GEMINI_API_KEY = "sua_chave_gemini_aqui"
   N8N_WEBHOOK_URL = "sua_url_n8n_aqui"
   N8N_WEBHOOK_SECRET = "seu_secret_aqui"
   ```

4. **Deploy:**
   - Clique em "Deploy"
   - Sua aplicação estará disponível em `https://seu-app.streamlit.app`

---

## ⚙️ Configurações Específicas

### 🔑 Obtendo Chave do Google Gemini

1. Acesse [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Clique em "Create API Key"
3. Copie a chave gerada
4. Use nas variáveis de ambiente

### 🌐 Configurando n8n (Opcional)

Para usar análise com IA via n8n:

1. **Deploy n8n:**
   - Use Railway, Heroku ou VPS
   - Configure webhook público

2. **Configurar Workflow:**
   - Importe `n8n-workflow-example.json`
   - Configure credenciais do Gemini
   - Ative o workflow

3. **Atualizar URLs:**
   - `N8N_WEBHOOK_URL`: URL pública do seu n8n
   - `N8N_WEBHOOK_SECRET`: Secret configurado no webhook

---

## 🧪 Testando o Deploy

### ✅ Vercel
```bash
# Testar API
curl -X POST https://seu-projeto.vercel.app/api/analisar \
  -H "Content-Type: application/json" \
  -d '{"website_url": "https://google.com"}'

# Testar status IA
curl https://seu-projeto.vercel.app/api/ai-status
```

### ✅ Streamlit
1. Acesse sua URL do Streamlit
2. Digite uma URL de teste
3. Configure o backend URL (se usando backend local)
4. Clique em "Analisar"

---

## 📋 Limitações Conhecidas

- **Selenium não funciona** em ambiente serverless (Vercel)
- **Instagram scraping** desabilitado na versão Vercel
- **Análise Google** pode ter limitações de rate limiting

## 🔧 Arquivos de Dependências

- **`requirements.txt`** - Para Streamlit Cloud (sem Flask/Selenium)
- **`requirements-vercel.txt`** - Para Vercel (sem Selenium)

## 🚨 Troubleshooting - Erro de Dependências

Se você encontrar o erro:
```
❗️ installer returned a non-zero exit code
❗️ Error during processing dependencies!
```

**Soluções:**
1. **Streamlit:** Use apenas `requirements.txt` (já otimizado)
2. **Vercel:** Use `requirements-vercel.txt` (configurado no vercel.json)
3. **Reinicie o app** no painel do Streamlit Cloud
4. **Verifique as versões** das dependências se o erro persistir

## 🔧 Troubleshooting

### ❌ Problemas Comuns

**Vercel - Build Failed:**
- Verifique se `requirements.txt` está na raiz
- Confirme se todas as dependências estão listadas
- Verifique logs de build na Vercel

**Streamlit - App Crashed:**
- Verifique se `streamlit_app.py` está na raiz
- Confirme configuração de secrets
- Verifique logs no painel do Streamlit

**API Errors:**
- Verifique variáveis de ambiente
- Confirme se chaves API são válidas
- Teste endpoints individualmente

### 🔍 Debug

**Logs Vercel:**
```bash
vercel logs seu-projeto.vercel.app
```

**Logs Streamlit:**
- Disponíveis no painel web do Streamlit Cloud

---

## 📈 Monitoramento

### 📊 Métricas Vercel
- Analytics automático
- Logs de função
- Métricas de performance

### 📊 Métricas Streamlit
- Viewer analytics
- App health status
- Usage statistics

---

## 🚀 Próximos Passos

1. **Configurar domínio customizado** (Vercel)
2. **Implementar cache Redis** (para produção)
3. **Configurar monitoramento** (Sentry, LogRocket)
4. **Otimizar performance** (CDN, compressão)
5. **Implementar CI/CD** (GitHub Actions)

---

## 📞 Suporte

Para problemas específicos:
- **Vercel:** [Documentação oficial](https://vercel.com/docs)
- **Streamlit:** [Documentação oficial](https://docs.streamlit.io)
- **Issues:** Abra uma issue no repositório GitHub

**Deploy realizado com sucesso! 🎉**