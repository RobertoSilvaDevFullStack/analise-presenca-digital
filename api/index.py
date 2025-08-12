from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import sys
from datetime import datetime
import json
import traceback

# Adicionar o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Importar módulos do backend
try:
    from scraper_modules.website_scraper import WebsiteScraper
    from scraper_modules.google_scraper import GoogleScraper
except ImportError as e:
    print(f"Erro ao importar módulos: {e}")
    WebsiteScraper = None
    GoogleScraper = None

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# Configurar CORS para Vercel
CORS(app, resources={
    r"/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept"]
    }
})

class AnalysisEngine:
    @staticmethod
    def analyze_website_data(website_data):
        """Analisa dados do website e gera insights"""
        if not website_data or 'error' in website_data:
            return {
                'score': 0,
                'status': 'error',
                'insights': ['Não foi possível analisar o website'],
                'recommendations': ['Verifique se a URL está correta e acessível']
            }
        
        score = 50  # Score base
        insights = []
        recommendations = []
        
        # Análise do título
        title = website_data.get('title', '')
        if title:
            if len(title) > 60:
                insights.append('Título muito longo (pode ser cortado nos resultados de busca)')
                recommendations.append('Reduza o título para menos de 60 caracteres')
                score -= 5
            elif len(title) < 30:
                insights.append('Título muito curto (pode não ser descritivo o suficiente)')
                recommendations.append('Expanda o título para ser mais descritivo')
                score -= 3
            else:
                insights.append('Título tem tamanho adequado')
                score += 10
        else:
            insights.append('Título não encontrado')
            recommendations.append('Adicione um título descritivo à página')
            score -= 15
        
        # Análise da descrição
        description = website_data.get('description', '')
        if description:
            if len(description) > 160:
                insights.append('Meta descrição muito longa')
                recommendations.append('Reduza a meta descrição para menos de 160 caracteres')
                score -= 5
            elif len(description) < 120:
                insights.append('Meta descrição muito curta')
                recommendations.append('Expanda a meta descrição para ser mais informativa')
                score -= 3
            else:
                insights.append('Meta descrição tem tamanho adequado')
                score += 10
        else:
            insights.append('Meta descrição não encontrada')
            recommendations.append('Adicione uma meta descrição atrativa')
            score -= 10
        
        # Análise de imagens
        images = website_data.get('images', [])
        if images:
            images_without_alt = sum(1 for img in images if not img.get('alt'))
            if images_without_alt > 0:
                insights.append(f'{images_without_alt} imagens sem texto alternativo')
                recommendations.append('Adicione texto alternativo a todas as imagens')
                score -= min(images_without_alt * 2, 10)
            else:
                insights.append('Todas as imagens têm texto alternativo')
                score += 5
        
        # Análise de links
        links = website_data.get('links', [])
        if links:
            external_links = sum(1 for link in links if link.get('external', False))
            if external_links > 0:
                insights.append(f'{external_links} links externos encontrados')
                score += min(external_links, 5)
        
        # Garantir que o score esteja entre 0 e 100
        score = max(0, min(100, score))
        
        return {
            'score': score,
            'status': 'completed',
            'insights': insights,
            'recommendations': recommendations,
            'details': {
                'title_length': len(title) if title else 0,
                'description_length': len(description) if description else 0,
                'images_count': len(images),
                'links_count': len(links)
            }
        }

@app.route('/api/analisar', methods=['POST', 'OPTIONS'])
def analisar():
    """Endpoint principal para análise de websites"""
    # Handle preflight CORS request
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type deve ser application/json'}), 400
        
        data = request.json
        if not data:
            return jsonify({'error': 'Dados JSON inválidos'}), 400
        
        website_url = data.get('website_url', '').strip()
        incluir_google = data.get('incluir_google', True)
        incluir_instagram = data.get('incluir_instagram', False)
        
        print(f"🔍 Analisando: {website_url}")
        
        if not website_url:
            return jsonify({'error': 'URL do website deve ser fornecido'}), 400
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'website_url': website_url,
            'success': True
        }
        
        # Análise do website
        if WebsiteScraper:
            try:
                scraper = WebsiteScraper()
                website_data = scraper.scrape(website_url)
                result['website_analysis'] = {
                    'raw_data': website_data,
                    'analysis': AnalysisEngine.analyze_website_data(website_data)
                }
                print("✅ Análise do website concluída")
            except Exception as e:
                print(f"❌ Erro na análise do website: {e}")
                result['website_analysis'] = {
                    'error': str(e),
                    'analysis': AnalysisEngine.analyze_website_data(None)
                }
        else:
            result['website_analysis'] = {
                'error': 'WebsiteScraper não disponível',
                'analysis': AnalysisEngine.analyze_website_data(None)
            }
        
        # Análise do Google (se solicitada)
        if incluir_google and GoogleScraper:
            try:
                google_scraper = GoogleScraper()
                google_data = google_scraper.search(website_url)
                result['google_results'] = google_data
                print("✅ Análise do Google concluída")
            except Exception as e:
                print(f"❌ Erro na análise do Google: {e}")
                result['google_results'] = {'error': str(e)}
        elif incluir_google:
            result['google_results'] = {'error': 'GoogleScraper não disponível'}
        
        # Análise do Instagram (placeholder)
        if incluir_instagram:
            result['instagram_data'] = {
                'message': 'Análise do Instagram não implementada na versão Vercel',
                'reason': 'Selenium não suportado em ambiente serverless'
            }
        
        return jsonify(result)
    
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        print(traceback.format_exc())
        return jsonify({
            'error': 'Erro interno do servidor',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/ai-status', methods=['GET'])
def ai_status():
    """Verifica o status da configuração de IA"""
    try:
        gemini_key = os.getenv('GEMINI_API_KEY')
        n8n_url = os.getenv('N8N_WEBHOOK_URL')
        n8n_secret = os.getenv('N8N_WEBHOOK_SECRET')
        
        gemini_configured = bool(gemini_key and gemini_key != 'your_gemini_api_key_here')
        n8n_configured = bool(n8n_url and n8n_url != 'http://n8n:5678')
        n8n_webhook_configured = bool(n8n_secret and n8n_secret != 'your_secure_webhook_secret_here')
        
        ai_ready = gemini_configured and n8n_configured and n8n_webhook_configured
        
        status = "ok" if ai_ready else "warning"
        message = "IA totalmente configurada" if ai_ready else "IA parcialmente configurada"
        
        return jsonify({
            'status': status,
            'message': message,
            'ai_configured': ai_ready,
            'details': {
                'gemini_key_set': gemini_configured,
                'n8n_configured': n8n_configured,
                'n8n_webhook_set': n8n_webhook_configured
            },
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao verificar status da IA: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'API funcionando',
        'timestamp': datetime.now().isoformat(),
        'environment': 'vercel'
    })

@app.route('/api', methods=['GET'])
def api_info():
    """Informações da API"""
    return jsonify({
        'name': 'Análise de Presença Digital API',
        'version': '1.0.0',
        'environment': 'vercel',
        'endpoints': {
            'POST /api/analisar': 'Análise completa de website',
            'GET /api/ai-status': 'Status da configuração de IA',
            'GET /api/health': 'Health check'
        },
        'timestamp': datetime.now().isoformat()
    })

# Para Vercel, exportar a aplicação
app = app

if __name__ == '__main__':
    app.run(debug=True)