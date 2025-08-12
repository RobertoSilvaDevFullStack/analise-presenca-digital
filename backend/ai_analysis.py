# ai_analysis.py - Módulo de integração com n8n e Gemini Pro

import requests
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIAnalysisEngine:
    """Engine para análises avançadas usando n8n + Gemini Pro"""
    
    def __init__(self):
        self.n8n_webhook_url = os.getenv('N8N_WEBHOOK_URL', 'http://n8n:5678')
        self.webhook_secret = os.getenv('N8N_WEBHOOK_SECRET', '')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY', '')
        self.timeout = 120  # 2 minutos para análise IA
        
    def analyze_with_ai(self, website_url: str, basic_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Realiza análise avançada usando IA"""
        try:
            logger.info(f"🤖 Iniciando análise IA para: {website_url}")
            
            # Preparar dados para envio
            payload = self._prepare_payload(website_url, basic_analysis)
            
            # Enviar para n8n workflow
            ai_result = self._send_to_n8n_workflow(payload)
            
            if ai_result.get('success', False):
                logger.info("✅ Análise IA concluída com sucesso")
                return self._format_ai_response(ai_result)
            else:
                logger.warning("⚠️ Análise IA falhou, usando fallback")
                return self._create_fallback_response(basic_analysis)
                
        except Exception as e:
            logger.error(f"❌ Erro na análise IA: {str(e)}")
            return self._create_error_response(str(e))
    
    def _prepare_payload(self, website_url: str, basic_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara dados para envio ao n8n"""
        return {
            'website_url': website_url,
            'timestamp': datetime.now().isoformat(),
            'analysis_type': 'comprehensive_ai',
            'basic_data': {
                'website_analysis': basic_analysis.get('website_analysis', {}),
                'google_analysis': basic_analysis.get('google_analysis', {}),
                'technical_data': self._extract_technical_data(basic_analysis),
                'content_data': self._extract_content_data(basic_analysis)
            },
            'ai_prompts': {
                'seo_analysis': self._get_seo_prompt(),
                'marketing_strategy': self._get_marketing_prompt(),
                'competitive_analysis': self._get_competitive_prompt()
            },
            'webhook_secret': self.webhook_secret
        }
    
    def _send_to_n8n_workflow(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Envia dados para workflow n8n"""
        webhook_url = f"{self.n8n_webhook_url}/webhook/analyze-website-ai"
        
        headers = {
            'Content-Type': 'application/json',
            'X-Webhook-Secret': self.webhook_secret
        }
        
        try:
            response = requests.post(
                webhook_url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"n8n retornou status {response.status_code}: {response.text}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except requests.exceptions.Timeout:
            logger.error("Timeout na comunicação com n8n")
            return {'success': False, 'error': 'Timeout'}
        except requests.exceptions.ConnectionError:
            logger.error("Erro de conexão com n8n")
            return {'success': False, 'error': 'Connection Error'}
        except Exception as e:
            logger.error(f"Erro inesperado: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _extract_technical_data(self, basic_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai dados técnicos para análise IA"""
        website_data = basic_analysis.get('website_analysis', {}).get('raw_data', {})
        
        return {
            'load_time': website_data.get('load_time', 0),
            'status_code': website_data.get('status_code', 0),
            'has_ssl': website_data.get('has_ssl', False),
            'cms_info': website_data.get('cms_info', 'Não identificado'),
            'meta_title': website_data.get('meta_title', ''),
            'meta_description': website_data.get('meta_description', ''),
            'h1_tags': website_data.get('h1_tags', []),
            'images_count': len(website_data.get('images', [])),
            'links_count': len(website_data.get('links', [])),
            'page_size': website_data.get('page_size', 0)
        }
    
    def _extract_content_data(self, basic_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai dados de conteúdo para análise IA"""
        website_data = basic_analysis.get('website_analysis', {}).get('raw_data', {})
        google_data = basic_analysis.get('google_analysis', {}).get('raw_data', {})
        
        return {
            'page_content': website_data.get('content', '')[:2000],  # Limitar conteúdo
            'meta_keywords': website_data.get('meta_keywords', ''),
            'social_media_links': website_data.get('social_media_links', []),
            'google_results_count': len(google_data.get('organic_results', [])),
            'competitor_domains': google_data.get('competitor_domains', []),
            'business_type': self._detect_business_type(website_data)
        }
    
    def _detect_business_type(self, website_data: Dict[str, Any]) -> str:
        """Detecta tipo de negócio baseado no conteúdo"""
        content = website_data.get('content', '').lower()
        title = website_data.get('meta_title', '').lower()
        
        business_keywords = {
            'hotel': ['hotel', 'pousada', 'resort', 'hospedagem', 'reserva'],
            'restaurante': ['restaurante', 'cardápio', 'delivery', 'comida'],
            'ecommerce': ['loja', 'comprar', 'carrinho', 'produto', 'preço'],
            'servicos': ['serviços', 'consultoria', 'atendimento', 'contato'],
            'saude': ['clínica', 'médico', 'saúde', 'tratamento', 'consulta'],
            'educacao': ['curso', 'escola', 'ensino', 'educação', 'aula']
        }
        
        for business_type, keywords in business_keywords.items():
            if any(keyword in content or keyword in title for keyword in keywords):
                return business_type
        
        return 'geral'
    
    def _get_seo_prompt(self) -> str:
        """Prompt especializado para análise SEO"""
        return """
        Analise os dados técnicos e de conteúdo fornecidos e crie uma análise SEO detalhada.
        
        Forneça:
        1. Análise técnica (performance, estrutura, meta tags)
        2. Análise de conteúdo (palavras-chave, estrutura de headings)
        3. Oportunidades de melhoria específicas
        4. Estratégia de palavras-chave recomendada
        5. Plano de ação priorizado (30, 60, 90 dias)
        
        Formato de resposta: JSON estruturado com scores de 0-100 para cada área.
        """
    
    def _get_marketing_prompt(self) -> str:
        """Prompt para estratégia de marketing digital"""
        return """
        Com base na análise do website e presença digital, crie uma estratégia de marketing completa.
        
        Inclua:
        1. Análise da presença digital atual
        2. Estratégia de conteúdo personalizada
        3. Campanhas Google Ads recomendadas
        4. Estratégia de redes sociais
        5. Métricas de acompanhamento (KPIs)
        6. Estimativa de investimento mensal
        
        Considere o tipo de negócio identificado e adapte as recomendações.
        
        Formato: JSON com estratégias priorizadas e cronograma.
        """
    
    def _get_competitive_prompt(self) -> str:
        """Prompt para análise competitiva"""
        return """
        Analise a posição competitiva do website no mercado.
        
        Forneça:
        1. Análise de gaps competitivos
        2. Oportunidades de diferenciação
        3. Benchmarks do setor
        4. Estratégias para superar concorrentes
        5. Nichos de mercado inexplorados
        
        Formato: JSON com insights acionáveis e scores competitivos.
        """
    
    def _format_ai_response(self, ai_result: Dict[str, Any]) -> Dict[str, Any]:
        """Formata resposta da IA para o frontend"""
        return {
            'success': True,
            'analysis_type': 'ai_enhanced',
            'timestamp': datetime.now().isoformat(),
            'seo_analysis': ai_result.get('seo_analysis', {}),
            'marketing_strategy': ai_result.get('marketing_strategy', {}),
            'competitive_analysis': ai_result.get('competitive_analysis', {}),
            'overall_score': ai_result.get('overall_score', 0),
            'priority_actions': ai_result.get('priority_actions', []),
            'estimated_impact': ai_result.get('estimated_impact', {}),
            'ai_confidence': ai_result.get('confidence_score', 0.8)
        }
    
    def _create_fallback_response(self, basic_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Cria resposta de fallback quando IA falha"""
        return {
            'success': True,
            'analysis_type': 'basic_enhanced',
            'timestamp': datetime.now().isoformat(),
            'message': 'Análise realizada com algoritmos básicos (IA temporariamente indisponível)',
            'basic_analysis': basic_analysis,
            'recommendations': self._generate_basic_recommendations(basic_analysis),
            'fallback': True
        }
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Cria resposta de erro"""
        return {
            'success': False,
            'analysis_type': 'error',
            'timestamp': datetime.now().isoformat(),
            'error': error_message,
            'message': 'Erro na análise. Tente novamente ou use a análise básica.'
        }
    
    def _generate_basic_recommendations(self, basic_analysis: Dict[str, Any]) -> list:
        """Gera recomendações básicas quando IA não está disponível"""
        recommendations = []
        
        website_data = basic_analysis.get('website_analysis', {}).get('raw_data', {})
        
        # Recomendações baseadas em dados técnicos
        if website_data.get('load_time', 0) > 3:
            recommendations.append({
                'type': 'performance',
                'priority': 'high',
                'title': 'Otimização de Performance',
                'description': 'Site com tempo de carregamento elevado. Otimize imagens e implemente cache.'
            })
        
        if not website_data.get('has_ssl', False):
            recommendations.append({
                'type': 'security',
                'priority': 'critical',
                'title': 'Implementar SSL',
                'description': 'Site sem certificado SSL. Implementação urgente necessária.'
            })
        
        if not website_data.get('meta_description'):
            recommendations.append({
                'type': 'seo',
                'priority': 'medium',
                'title': 'Meta Description',
                'description': 'Adicionar meta descriptions para melhorar SEO.'
            })
        
        return recommendations

# Função auxiliar para integração com app.py
def perform_ai_analysis(website_url: str, basic_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Função principal para análise com IA"""
    ai_engine = AIAnalysisEngine()
    return ai_engine.analyze_with_ai(website_url, basic_analysis)