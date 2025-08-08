from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import os
from datetime import datetime
from supabase import create_client, Client
from scraper_modules.website_scraper import WebsiteScraper
from scraper_modules.google_scraper import GoogleScraper
import json
import traceback

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# Configurar CORS mais permissivo
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost", "http://localhost:80", "http://127.0.0.1", "http://0.0.0.0"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept"]
    }
})

# Configurar Supabase - com verificação
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

if supabase_url and supabase_key:
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Supabase configurado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao configurar Supabase: {e}")
        supabase = None
else:
    print("⚠️  Supabase não configurado - variáveis de ambiente não encontradas")
    supabase = None

class AnalysisEngine:
    @staticmethod
    def analyze_website_data(website_data):
        """Analisa dados do website e gera relatório profissional"""
        url = website_data.get('url', 'Site analisado')
        
        # Análise da estrutura e desenvolvedor
        estrutura_info = []
        cms_info = website_data.get('cms_detected', 'Não identificado')
        developer_info = website_data.get('developer_info', 'Não identificado')
        
        if cms_info != 'Não identificado':
            estrutura_info.append(f"O site utiliza {cms_info} como plataforma.")
        else:
            estrutura_info.append("Não foi possível identificar publicamente a plataforma (CMS) utilizada.")
        
        if developer_info != 'Não identificado':
            estrutura_info.append(f"Desenvolvido por: {developer_info}.")
        else:
            estrutura_info.append("Não foi possível identificar publicamente a empresa desenvolvedora do site.")
        
        # Análise técnica
        load_time = website_data.get('load_time', 0)
        has_ssl = website_data.get('has_ssl', False)
        status_code = website_data.get('status_code', 0)
        
        if status_code == 200:
            estrutura_info.append("O site está funcionalmente ativo e bem organizado.")
        
        if has_ssl:
            estrutura_info.append("Possui certificado SSL (HTTPS) implementado.")
        else:
            estrutura_info.append("⚠️ Site sem certificado SSL - vulnerabilidade de segurança.")
        
        estrutura_desc = " ".join(estrutura_info)
        
        # Melhorias identificadas
        melhorias = []
        
        # SEO e Performance
        if load_time > 3:
            melhorias.append("**Otimização de Performance**: O tempo de carregamento está acima do recomendado (>3s). Recomenda-se otimização de imagens, implementação de cache e minificação de recursos para melhorar a experiência do usuário e o ranking no Google.")
        else:
            melhorias.append("**Otimização para SEO**: Implementar estratégias de SEO técnico e de conteúdo. Criar um calendário editorial focado em palavras-chave relevantes para o negócio, otimizar meta descrições e titles, e desenvolver conteúdo que responda às dúvidas do público-alvo.")
        
        # CRO (Conversion Rate Optimization)
        melhorias.append("**Otimização de Conversão (CRO)**: Análise detalhada do funil de conversão para identificar pontos de atrito. Implementação de CTAs mais proeminentes, otimização de formulários e criação de landing pages específicas para diferentes campanhas.")
        
        # Conteúdo e UX
        melhorias.append("**Experiência do Usuário (UX)**: Melhoria na navegabilidade e criação de conteúdo visual mais envolvente. Implementação de chatbots, depoimentos de clientes e elementos de prova social para aumentar a confiança e conversão.")
        
        # Marketing Digital
        necessidades = []
        necessidades.append("**Google Ads e Hotel Ads**: Não foram identificados anúncios pagos com o nome da empresa. Isso permite que OTA's (Online Travel Agencies) capturem reservas de usuários que já procuram especificamente pelo negócio.")
        necessidades.append("**Presença Digital**: Análise completa da presença digital revela oportunidades de melhoria na estratégia de marketing digital integrada.")
        
        return {
            'estrutura_desenvolvedor': estrutura_desc,
            'melhorias_identificadas': melhorias,
            'necessidades_identificadas': necessidades
        }
    
    @staticmethod
    def analyze_google_data(google_data):
        """Analisa dados do Google e gera relatório profissional"""
        url = google_data.get('url', 'Site analisado')
        google_analysis = google_data.get('google_analysis', {})
        recommendations = google_data.get('recommendations', {})
        
        # Análise de SEO
        seo_status = google_analysis.get('seo_status', {})
        seo_info = []
        if isinstance(seo_status, dict):
            status = seo_status.get('status', 'Não avaliado')
            seo_info.append(f"Status SEO: {status}")
            
            priority_actions = seo_status.get('priority_actions', [])
            if priority_actions:
                seo_info.append("Ações prioritárias: " + ", ".join(priority_actions))
        
        # Análise de presença social
        social_presence = google_analysis.get('social_presence', {})
        social_info = []
        if isinstance(social_presence, dict):
            platforms = social_presence.get('platforms_found', [])
            if platforms:
                social_info.append(f"Plataformas encontradas: {', '.join(platforms)}")
            else:
                social_info.append("**⚠️ Presença limitada nas redes sociais detectada**")
            
            social_recommendations = social_presence.get('recommendations', [])
            if social_recommendations:
                social_info.extend(social_recommendations)
        
        # Análise de anúncios
        ads_presence = google_analysis.get('ads_presence', {})
        ads_info = []
        if isinstance(ads_presence, dict):
            ads_status = ads_presence.get('status', 'Não avaliado')
            ads_info.append(f"Presença publicitária: {ads_status}")
            
            opportunities = ads_presence.get('opportunities', [])
            if opportunities:
                ads_info.append("Oportunidades identificadas:")
                ads_info.extend([f"• {opp}" for opp in opportunities])
        
        # Análise de reputação
        reputation = google_analysis.get('online_reputation', {})
        reputation_info = []
        if isinstance(reputation, dict):
            rep_status = reputation.get('status', 'Não avaliado')
            reputation_info.append(f"Reputação online: {rep_status}")
            
            reviews_count = reputation.get('reviews_count', 0)
            if reviews_count > 0:
                sentiment = reputation.get('sentiment', 'Neutro')
                reputation_info.append(f"Avaliações encontradas: {reviews_count} (Sentimento: {sentiment})")
        
        # Análise de mercado
        market_position = google_analysis.get('market_position', {})
        market_info = []
        if isinstance(market_position, dict):
            competitors = market_position.get('competitors_identified', 0)
            if competitors > 0:
                market_info.append(f"Concorrentes identificados: {competitors}")
            
            market_status = market_position.get('market_status', '')
            if market_status:
                market_info.append(f"Status do mercado: {market_status}")
        
        # Estratégias recomendadas baseadas no Google
        estrategias_google = []
        
        # SEO
        seo_improvements = recommendations.get('seo_improvements', [])
        if seo_improvements:
            estrategias_google.append("**SEO e Visibilidade Online**:")
            estrategias_google.extend([f"• {imp}" for imp in seo_improvements[:3]])
        
        # Marketing Digital
        digital_marketing = recommendations.get('digital_marketing', [])
        if digital_marketing:
            estrategias_google.append("**Marketing Digital**:")
            estrategias_google.extend([f"• {dm}" for dm in digital_marketing[:3]])
        
        # Melhorias no site
        website_improvements = recommendations.get('website_improvements', [])
        if website_improvements:
            estrategias_google.append("**Melhorias no Website**:")
            estrategias_google.extend([f"• {wi}" for wi in website_improvements[:3]])
        
        return {
            'seo_analise': " ".join(seo_info) if seo_info else "Análise SEO não disponível",
            'presenca_social': " ".join(social_info) if social_info else "Análise de redes sociais não disponível",
            'presenca_publicitaria': " ".join(ads_info) if ads_info else "Análise publicitária não disponível",
            'reputacao_online': " ".join(reputation_info) if reputation_info else "Análise de reputação não disponível",
            'posicao_mercado': " ".join(market_info) if market_info else "Análise de mercado não disponível",
            'estrategias_google': estrategias_google
        }
    
    @staticmethod
    def _format_number(num):
        """Formata números para exibição"""
        if num is None:
            return "N/A"
        if num >= 1000000:
            return f"{num/1000000:.1f}M"
        elif num >= 1000:
            return f"{num/1000:.1f}K"
        else:
            return str(num)

@app.route('/analisar', methods=['POST', 'OPTIONS'])
def analisar():
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
        
        print(f"📝 Recebida requisição - Site: {website_url}")
        
        if not website_url:
            return jsonify({'error': 'URL do website deve ser fornecido'}), 400
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'website_analysis': None,
            'google_analysis': None
        }
        
        # Análise do Website
        if website_url:
            print(f"🔍 Iniciando análise do website: {website_url}")
            try:
                website_scraper = WebsiteScraper()
                website_data = website_scraper.scrape(website_url)
                website_analysis = AnalysisEngine.analyze_website_data(website_data)
                
                result['website_analysis'] = {
                    'url': website_url,
                    'raw_data': website_data,
                    'relatorio': {
                        'titulo': f"Análise do Site: {website_url}",
                        'estrutura_desenvolvedor': website_analysis['estrutura_desenvolvedor'],
                        'melhorias_identificadas': website_analysis['melhorias_identificadas'],
                        'necessidades_identificadas': website_analysis['necessidades_identificadas']
                    }
                }
                print("✅ Análise do website concluída")
            except Exception as e:
                print(f"❌ Erro na análise do website: {e}")
                result['website_analysis'] = {
                    'url': website_url,
                    'raw_data': {'error': f'Erro ao analisar website: {str(e)}'},
                    'relatorio': {
                        'titulo': f"Análise do Site: {website_url}",
                        'estrutura_desenvolvedor': 'Não foi possível analisar a estrutura do site devido a problemas técnicos.',
                        'melhorias_identificadas': ['Recomenda-se uma análise técnica manual para identificar oportunidades de melhoria.'],
                        'necessidades_identificadas': ['Verificação técnica necessária para diagnóstico completo.']
                    }
                }
        
        # Análise do Google
        print(f"🔍 Iniciando análise do Google para: {website_url}")
        try:
            google_scraper = GoogleScraper()
            google_data = google_scraper.search_website_info(website_url)
            google_analysis = AnalysisEngine.analyze_google_data(google_data)
            
            result['google_analysis'] = {
                'url': website_url,
                'raw_data': google_data,
                'relatorio': {
                    'titulo': f"Análise do Google: {website_url}",
                    'seo_analise': google_analysis['seo_analise'],
                    'presenca_social': google_analysis['presenca_social'],
                    'presenca_publicitaria': google_analysis['presenca_publicitaria'],
                    'reputacao_online': google_analysis['reputacao_online'],
                    'posicao_mercado': google_analysis['posicao_mercado'],
                    'estrategias_google': google_analysis['estrategias_google']
                }
            }
            print("✅ Análise do Google concluída")
        except Exception as e:
            print(f"❌ Erro na análise do Google: {e}")
            result['google_analysis'] = {
                'url': website_url,
                'raw_data': {'error': f'Erro ao analisar no Google: {str(e)}'},
                'relatorio': {
                    'titulo': f"Análise do Google: {website_url}",
                    'seo_analise': 'Não foi possível realizar análise SEO via Google.',
                    'presenca_social': 'Análise de presença social não disponível.',
                    'presenca_publicitaria': 'Análise publicitária não disponível.',
                    'reputacao_online': 'Análise de reputação não disponível.',
                    'posicao_mercado': 'Análise de mercado não disponível.',
                    'estrategias_google': ['Recomenda-se análise manual para estratégias personalizadas.']
                }
            }
        
        # Salvar no Supabase (se configurado)
        if supabase:
            try:
                supabase.table('analyses').insert({
                    'website_url': website_url or None,
                    'instagram_url': instagram_url or None,
                    'analysis_data': result,
                    'created_at': datetime.now().isoformat()
                }).execute()
                print("✅ Dados salvos no Supabase")
            except Exception as db_error:
                print(f"⚠️  Erro ao salvar no banco (continuando): {db_error}")
        else:
            print("⚠️  Supabase não configurado - dados não salvos")
        
        return jsonify(result)
    
    except Exception as e:
        error_msg = f'Erro interno do servidor: {str(e)}'
        print(f"❌ {error_msg}")
        print(f"🔍 Traceback: {traceback.format_exc()}")
        return jsonify({'error': error_msg}), 500

@app.route('/relatorio-crm', methods=['POST', 'OPTIONS'])
def relatorio_crm():
    """Gera relatório formatado para CRM RD Station"""
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
        instagram_url = data.get('instagram_url', '').strip()
        
        if not website_url and not instagram_url:
            return jsonify({'error': 'Pelo menos um URL deve ser fornecido'}), 400
        
        print(f"📋 Gerando relatório CRM - Site: {website_url}, Instagram: {instagram_url}")
        
        # Executar análise diretamente
        result = {
            'timestamp': datetime.now().isoformat(),
            'website_analysis': None,
            'instagram_analysis': None
        }
        
        # Análise do Website
        if website_url:
            print(f"🔍 Iniciando análise do website: {website_url}")
            try:
                website_scraper = WebsiteScraper()
                website_data = website_scraper.scrape(website_url)
                website_analysis = AnalysisEngine.analyze_website_data(website_data)
                
                result['website_analysis'] = {
                    'url': website_url,
                    'raw_data': website_data,
                    'relatorio': {
                        'titulo': f"Análise do Site: {website_url}",
                        'estrutura_desenvolvedor': website_analysis['estrutura_desenvolvedor'],
                        'melhorias_identificadas': website_analysis['melhorias_identificadas'],
                        'necessidades_identificadas': website_analysis['necessidades_identificadas']
                    }
                }
                print("✅ Análise do website concluída")
            except Exception as e:
                print(f"❌ Erro na análise do website: {e}")
                result['website_analysis'] = {
                    'url': website_url,
                    'raw_data': {'error': f'Erro ao analisar website: {str(e)}'},
                    'relatorio': {
                        'titulo': f"Análise do Site: {website_url}",
                        'estrutura_desenvolvedor': 'Não foi possível analisar a estrutura do site devido a problemas técnicos.',
                        'melhorias_identificadas': ['Recomenda-se uma análise técnica manual para identificar oportunidades de melhoria.'],
                        'necessidades_identificadas': ['Verificação técnica necessária para diagnóstico completo.']
                    }
                }
        
        # Análise do Instagram
        if instagram_url:
            print(f"📱 Iniciando análise do Instagram: {instagram_url}")
            instagram_scraper = None
            try:
                instagram_scraper = InstagramScraper()
                if not instagram_scraper.driver:
                    raise Exception("Driver do Selenium não disponível")
                
                instagram_data = instagram_scraper.scrape(instagram_url)
                instagram_analysis = AnalysisEngine.analyze_instagram_data(instagram_data)
                
                result['instagram_analysis'] = {
                    'url': instagram_url,
                    'raw_data': instagram_data,
                    'relatorio': {
                        'titulo': f"Análise do Instagram: @{instagram_data.get('username', instagram_url)}",
                        'perfil_analise': instagram_analysis['perfil_analise'],
                        'atividade_status': instagram_analysis['atividade_status'],
                        'tipo_conta': instagram_analysis['tipo_conta'],
                        'bio_status': instagram_analysis['bio_status'],
                        'estrategias_recomendadas': instagram_analysis['estrategias_recomendadas']
                    }
                }
                print("✅ Análise do Instagram concluída")
            except Exception as e:
                print(f"❌ Erro na análise do Instagram: {e}")
                result['instagram_analysis'] = {
                    'url': instagram_url,
                    'raw_data': {'error': f'Erro ao analisar Instagram: {str(e)}'},
                    'relatorio': {
                        'titulo': f"Análise do Instagram: {instagram_url}",
                        'perfil_analise': 'Não foi possível analisar o perfil devido a limitações técnicas.',
                        'atividade_status': 'Status de atividade não disponível.',
                        'tipo_conta': 'Não identificado',
                        'bio_status': 'Não foi possível verificar',
                        'estrategias_recomendadas': ['Recomenda-se análise manual do perfil para estratégias personalizadas.']
                    }
                }
            finally:
                # Garantir que o driver seja fechado
                if instagram_scraper:
                    instagram_scraper.close_driver()
        
        # Gerar relatório formatado
        relatorio_texto = gerar_relatorio_texto(result, website_url, instagram_url)
        
        return jsonify({
            'relatorio_crm': relatorio_texto,
            'dados_completos': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        error_msg = f'Erro interno do servidor: {str(e)}'
        print(f"❌ {error_msg}")
        print(f"🔍 Traceback: {traceback.format_exc()}")
        return jsonify({'error': error_msg}), 500

def gerar_relatorio_texto(analysis_data, website_url, instagram_url):
    """Gera relatório em texto formatado para CRM"""
    relatorio = []
    
    # Análise do Website
    if website_url and analysis_data.get('website_analysis'):
        website_rel = analysis_data['website_analysis'].get('relatorio', {})
        
        relatorio.append(f"Análise do Site: {website_url}")
        relatorio.append("")
        
        # Estrutura e Desenvolvedor
        estrutura = website_rel.get('estrutura_desenvolvedor', 'Não foi possível analisar a estrutura.')
        relatorio.append(f"Estrutura e Desenvolvedor: {estrutura}")
        relatorio.append("")
        
        # Melhorias
        melhorias = website_rel.get('melhorias_identificadas', [])
        if melhorias:
            relatorio.append("Melhorias a serem realizadas:")
            relatorio.append("")
            for i, melhoria in enumerate(melhorias, 1):
                relatorio.append(f"{melhoria}")
                relatorio.append("")
        
        # Necessidades
        necessidades = website_rel.get('necessidades_identificadas', [])
        if necessidades:
            relatorio.append("Algumas necessidades já identificadas:")
            relatorio.append("")
            for necessidade in necessidades:
                relatorio.append(f"{necessidade}")
                relatorio.append("")
    
    # Análise do Instagram
    if instagram_url and analysis_data.get('instagram_analysis'):
        instagram_rel = analysis_data['instagram_analysis'].get('relatorio', {})
        
        relatorio.append(f"Análise do Instagram: {instagram_url}")
        relatorio.append("")
        
        # Status do perfil
        perfil_analise = instagram_rel.get('perfil_analise', '')
        if perfil_analise:
            relatorio.append(f"Status do Perfil: {perfil_analise}")
            relatorio.append("")
        
        # Atividade
        atividade = instagram_rel.get('atividade_status', '')
        if atividade and 'sem atividade' in atividade.lower():
            relatorio.append(atividade)
            relatorio.append("")
        
        # Tipo de conta e bio
        tipo_conta = instagram_rel.get('tipo_conta', '')
        bio_status = instagram_rel.get('bio_status', '')
        if tipo_conta or bio_status:
            relatorio.append(f"Configuração: {tipo_conta}. {bio_status}")
            relatorio.append("")
        
        # Estratégias
        estrategias = instagram_rel.get('estrategias_recomendadas', [])
        if estrategias:
            relatorio.append("Estratégias Recomendadas para Instagram:")
            relatorio.append("")
            for estrategia in estrategias:
                relatorio.append(f"{estrategia}")
                relatorio.append("")
    
    # Conclusão personalizada
    relatorio.append("Com nosso meet, entregaremos um diagnóstico mais completo e uma proposta personalizada para alcançar novos resultados.")
    
    return "\n".join(relatorio)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Servidor funcionando'})

# Rotas para servir arquivos estáticos do frontend
@app.route('/')
def index():
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    return send_from_directory(frontend_path, 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    return send_from_directory(frontend_path, filename)

if __name__ == '__main__':
    print("🚀 Iniciando servidor Flask...")
    print(f"📍 Servidor rodará em: http://0.0.0.0:5000")
    print(f"📁 Frontend será servido de: {os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')}")
    app.run(host='0.0.0.0', port=5000, debug=True)