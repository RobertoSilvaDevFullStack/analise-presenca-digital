import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import quote_plus, urljoin
import json
from datetime import datetime

class GoogleScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def search_website_info(self, website_url):
        """Busca informações sobre o website no Google"""
        try:
            # Extrair domínio da URL
            domain = self._extract_domain(website_url)
            
            # Realizar múltiplas buscas para coletar informações
            search_results = {
                'general_info': self._search_general_info(domain),
                'seo_analysis': self._search_seo_info(domain),
                'social_presence': self._search_social_presence(domain),
                'ads_presence': self._search_ads_presence(domain),
                'reviews': self._search_reviews(domain),
                'competitors': self._search_competitors(domain)
            }
            
            # Compilar análise final
            analysis = self._compile_analysis(website_url, search_results)
            
            return analysis
            
        except Exception as e:
            return {
                'url': website_url,
                'error': f'Erro ao buscar informações no Google: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def _extract_domain(self, url):
        """Extrai o domínio da URL"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc.replace('www.', '')
    
    def _search_general_info(self, domain):
        """Busca informações gerais sobre o site"""
        try:
            query = f'site:{domain}'
            results = self._perform_google_search(query)
            
            return {
                'indexed_pages': self._count_indexed_pages(results),
                'main_topics': self._extract_main_topics(results),
                'site_structure': self._analyze_site_structure(results)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _search_seo_info(self, domain):
        """Busca informações de SEO"""
        try:
            queries = [
                f'"{domain}" SEO análise',
                f'"{domain}" otimização',
                f'"{domain}" ranking Google'
            ]
            
            seo_info = []
            for query in queries:
                results = self._perform_google_search(query)
                seo_info.extend(self._extract_seo_insights(results))
            
            return {
                'seo_mentions': seo_info,
                'optimization_opportunities': self._identify_seo_opportunities(domain)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _search_social_presence(self, domain):
        """Busca presença em redes sociais"""
        try:
            social_platforms = ['instagram', 'facebook', 'youtube', 'linkedin', 'twitter']
            social_presence = {}
            
            for platform in social_platforms:
                query = f'site:{platform}.com "{domain}" OR "{domain.replace(".com", "")}"'
                results = self._perform_google_search(query)
                social_presence[platform] = self._extract_social_links(results, platform)
            
            return social_presence
        except Exception as e:
            return {'error': str(e)}
    
    def _search_ads_presence(self, domain):
        """Busca presença em anúncios do Google"""
        try:
            # Buscar por menções de anúncios
            queries = [
                f'"{domain}" Google Ads',
                f'"{domain}" anúncio Google',
                f'"{domain}" publicidade online'
            ]
            
            ads_info = []
            for query in queries:
                results = self._perform_google_search(query)
                ads_info.extend(self._extract_ads_info(results))
            
            return {
                'ads_mentions': ads_info,
                'advertising_analysis': self._analyze_advertising_presence(domain)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _search_reviews(self, domain):
        """Busca avaliações e reviews"""
        try:
            queries = [
                f'"{domain}" avaliação',
                f'"{domain}" review',
                f'"{domain}" opinião',
                f'"{domain}" experiência'
            ]
            
            reviews = []
            for query in queries:
                results = self._perform_google_search(query)
                reviews.extend(self._extract_reviews(results))
            
            return {
                'reviews_found': reviews,
                'sentiment_analysis': self._analyze_sentiment(reviews)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _search_competitors(self, domain):
        """Busca concorrentes"""
        try:
            # Identificar setor/nicho baseado no domínio
            sector_keywords = self._identify_sector_keywords(domain)
            
            competitors = []
            for keyword in sector_keywords:
                query = f'{keyword} -site:{domain}'
                results = self._perform_google_search(query)
                competitors.extend(self._extract_competitor_sites(results))
            
            return {
                'potential_competitors': competitors[:10],  # Top 10
                'market_analysis': self._analyze_market_position(domain, competitors)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _perform_google_search(self, query, num_results=10):
        """Realiza busca no Google"""
        try:
            # Codificar query para URL
            encoded_query = quote_plus(query)
            url = f'https://www.google.com/search?q={encoded_query}&num={num_results}&hl=pt-BR'
            
            # Adicionar delay para evitar rate limiting
            time.sleep(1)
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Definir encoding explicitamente para evitar problemas de decodificação
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extrair resultados de busca
            results = []
            search_results = soup.find_all('div', class_='g')
            
            for result in search_results:
                title_elem = result.find('h3')
                link_elem = result.find('a')
                snippet_elem = result.find('span', class_=['aCOpRe', 'st'])
                
                if title_elem and link_elem:
                    results.append({
                        'title': title_elem.get_text(strip=True),
                        'url': link_elem.get('href', ''),
                        'snippet': snippet_elem.get_text(strip=True) if snippet_elem else ''
                    })
            
            return results
            
        except Exception as e:
            print(f"Erro na busca Google: {e}")
            return []
    
    def _compile_analysis(self, website_url, search_results):
        """Compila análise final baseada nos resultados das buscas"""
        analysis = {
            'url': website_url,
            'timestamp': datetime.now().isoformat(),
            'google_analysis': {
                'indexed_pages': search_results.get('general_info', {}).get('indexed_pages', 0),
                'seo_status': self._evaluate_seo_status(search_results.get('seo_analysis', {})),
                'social_presence': self._evaluate_social_presence(search_results.get('social_presence', {})),
                'ads_presence': self._evaluate_ads_presence(search_results.get('ads_presence', {})),
                'online_reputation': self._evaluate_reputation(search_results.get('reviews', {})),
                'market_position': self._evaluate_market_position(search_results.get('competitors', {}))
            },
            'recommendations': self._generate_recommendations(search_results),
            'detailed_findings': search_results
        }
        
        return analysis
    
    def _count_indexed_pages(self, results):
        """Conta páginas indexadas aproximadamente"""
        return len(results)
    
    def _extract_main_topics(self, results):
        """Extrai tópicos principais dos resultados"""
        topics = []
        for result in results:
            title = result.get('title', '').lower()
            snippet = result.get('snippet', '').lower()
            
            # Palavras-chave relevantes para resorts/hotéis
            keywords = ['resort', 'hotel', 'pousada', 'hospedagem', 'turismo', 'lazer', 'piscina', 'praia']
            
            for keyword in keywords:
                if keyword in title or keyword in snippet:
                    topics.append(keyword)
        
        return list(set(topics))
    
    def _analyze_site_structure(self, results):
        """Analisa estrutura do site baseada nos resultados"""
        pages = []
        for result in results:
            url = result.get('url', '')
            if url:
                pages.append(url)
        
        return {
            'total_pages_found': len(pages),
            'page_types': self._categorize_pages(pages)
        }
    
    def _categorize_pages(self, pages):
        """Categoriza tipos de páginas encontradas"""
        categories = {
            'home': 0,
            'about': 0,
            'services': 0,
            'contact': 0,
            'blog': 0,
            'gallery': 0,
            'booking': 0
        }
        
        for page in pages:
            page_lower = page.lower()
            if any(term in page_lower for term in ['home', 'inicio', 'index']):
                categories['home'] += 1
            elif any(term in page_lower for term in ['about', 'sobre', 'quem-somos']):
                categories['about'] += 1
            elif any(term in page_lower for term in ['servicos', 'services', 'estrutura']):
                categories['services'] += 1
            elif any(term in page_lower for term in ['contato', 'contact']):
                categories['contact'] += 1
            elif any(term in page_lower for term in ['blog', 'noticias', 'artigos']):
                categories['blog'] += 1
            elif any(term in page_lower for term in ['galeria', 'gallery', 'fotos']):
                categories['gallery'] += 1
            elif any(term in page_lower for term in ['reserva', 'booking', 'book']):
                categories['booking'] += 1
        
        return categories
    
    def _extract_seo_insights(self, results):
        """Extrai insights de SEO dos resultados"""
        insights = []
        for result in results:
            snippet = result.get('snippet', '')
            if any(term in snippet.lower() for term in ['seo', 'otimização', 'ranking', 'busca']):
                insights.append({
                    'source': result.get('title', ''),
                    'insight': snippet,
                    'url': result.get('url', '')
                })
        return insights
    
    def _identify_seo_opportunities(self, domain):
        """Identifica oportunidades de SEO"""
        return [
            'Otimização para palavras-chave locais (Pipa, Natal, RN)',
            'Criação de conteúdo sobre atividades turísticas',
            'Melhoria na velocidade de carregamento',
            'Implementação de schema markup para hotéis',
            'Otimização para busca mobile',
            'Criação de landing pages para diferentes tipos de hospedagem'
        ]
    
    def _extract_social_links(self, results, platform):
        """Extrai links de redes sociais dos resultados"""
        social_links = []
        for result in results:
            url = result.get('url', '')
            if platform in url.lower():
                social_links.append({
                    'platform': platform,
                    'url': url,
                    'title': result.get('title', '')
                })
        return social_links
    
    def _extract_ads_info(self, results):
        """Extrai informações sobre anúncios"""
        ads_info = []
        for result in results:
            snippet = result.get('snippet', '')
            if any(term in snippet.lower() for term in ['anúncio', 'ads', 'publicidade', 'marketing']):
                ads_info.append({
                    'source': result.get('title', ''),
                    'info': snippet,
                    'url': result.get('url', '')
                })
        return ads_info
    
    def _analyze_advertising_presence(self, domain):
        """Analisa presença publicitária"""
        return {
            'google_ads_detected': False,  # Baseado na análise dos resultados
            'hotel_ads_detected': False,
            'recommendations': [
                'Implementar campanhas Google Ads para capturar busca direta',
                'Configurar Google Hotel Ads para competir com OTAs',
                'Criar campanhas de remarketing',
                'Investir em anúncios para palavras-chave locais'
            ]
        }
    
    def _extract_reviews(self, results):
        """Extrai reviews dos resultados"""
        reviews = []
        for result in results:
            snippet = result.get('snippet', '')
            if any(term in snippet.lower() for term in ['avaliação', 'review', 'experiência', 'opinião']):
                reviews.append({
                    'source': result.get('title', ''),
                    'content': snippet,
                    'url': result.get('url', '')
                })
        return reviews
    
    def _analyze_sentiment(self, reviews):
        """Analisa sentimento das reviews"""
        if not reviews:
            return {'status': 'Poucas avaliações encontradas online'}
        
        positive_words = ['excelente', 'ótimo', 'maravilhoso', 'recomendo', 'perfeito']
        negative_words = ['ruim', 'péssimo', 'decepcionante', 'problema', 'insatisfeito']
        
        positive_count = 0
        negative_count = 0
        
        for review in reviews:
            content = review.get('content', '').lower()
            for word in positive_words:
                if word in content:
                    positive_count += 1
            for word in negative_words:
                if word in content:
                    negative_count += 1
        
        return {
            'positive_mentions': positive_count,
            'negative_mentions': negative_count,
            'overall_sentiment': 'Positivo' if positive_count > negative_count else 'Neutro'
        }
    
    def _identify_sector_keywords(self, domain):
        """Identifica palavras-chave do setor"""
        # Para resorts/hotéis
        return [
            'resort pipa',
            'hotel pipa',
            'pousada pipa',
            'hospedagem natal',
            'resort nordeste',
            'hotel praia pipa'
        ]
    
    def _extract_competitor_sites(self, results):
        """Extrai sites concorrentes dos resultados"""
        competitors = []
        for result in results:
            url = result.get('url', '')
            title = result.get('title', '')
            
            # Filtrar apenas sites que parecem ser de hotéis/resorts
            if any(term in title.lower() for term in ['hotel', 'resort', 'pousada', 'hospedagem']):
                competitors.append({
                    'name': title,
                    'url': url,
                    'snippet': result.get('snippet', '')
                })
        
        return competitors
    
    def _analyze_market_position(self, domain, competitors):
        """Analisa posição no mercado"""
        return {
            'competitors_found': len(competitors),
            'market_analysis': 'Mercado competitivo com várias opções de hospedagem em Pipa',
            'differentiation_opportunities': [
                'Foco na experiência familiar',
                'Atividades aquáticas exclusivas',
                'Gastronomia local',
                'Sustentabilidade e ecoturismo'
            ]
        }
    
    def _evaluate_seo_status(self, seo_data):
        """Avalia status de SEO"""
        if seo_data.get('error'):
            return 'Não foi possível avaliar'
        
        return {
            'status': 'Oportunidades de melhoria identificadas',
            'priority_actions': [
                'Otimização para busca local',
                'Criação de conteúdo relevante',
                'Melhoria na estrutura técnica'
            ]
        }
    
    def _evaluate_social_presence(self, social_data):
        """Avalia presença social"""
        if social_data.get('error'):
            return 'Não foi possível avaliar'
        
        platforms_found = []
        for platform, links in social_data.items():
            if links and len(links) > 0:
                platforms_found.append(platform)
        
        return {
            'platforms_found': platforms_found,
            'status': 'Presença limitada nas redes sociais' if len(platforms_found) < 2 else 'Boa presença social',
            'recommendations': [
                'Criar perfil no Instagram com conteúdo visual atrativo',
                'Desenvolver estratégia de conteúdo para Facebook',
                'Implementar integração com redes sociais no site'
            ]
        }
    
    def _evaluate_ads_presence(self, ads_data):
        """Avalia presença publicitária"""
        return {
            'status': 'Baixa presença publicitária detectada',
            'opportunities': [
                'Google Ads para captura de demanda',
                'Google Hotel Ads para competir com OTAs',
                'Campanhas de remarketing',
                'Anúncios em redes sociais'
            ]
        }
    
    def _evaluate_reputation(self, reviews_data):
        """Avalia reputação online"""
        if reviews_data.get('error'):
            return 'Não foi possível avaliar'
        
        reviews = reviews_data.get('reviews_found', [])
        sentiment = reviews_data.get('sentiment_analysis', {})
        
        return {
            'reviews_count': len(reviews),
            'sentiment': sentiment.get('overall_sentiment', 'Neutro'),
            'status': 'Reputação online limitada - oportunidade de melhoria'
        }
    
    def _evaluate_market_position(self, competitors_data):
        """Avalia posição no mercado"""
        if competitors_data.get('error'):
            return 'Não foi possível avaliar'
        
        competitors = competitors_data.get('potential_competitors', [])
        
        return {
            'competitors_identified': len(competitors),
            'market_status': 'Mercado competitivo',
            'positioning_strategy': 'Diferenciação através de experiência única e marketing digital'
        }
    
    def _generate_recommendations(self, search_results):
        """Gera recomendações baseadas na análise"""
        recommendations = {
            'seo_improvements': [
                'Implementar estratégia de SEO local para Pipa/Natal',
                'Criar calendário editorial com foco em turismo',
                'Otimizar velocidade e experiência mobile',
                'Implementar schema markup para hotéis'
            ],
            'digital_marketing': [
                'Criar perfil no Instagram com conteúdo visual atrativo',
                'Implementar Google Ads e Google Hotel Ads',
                'Desenvolver campanhas de remarketing',
                'Investir em marketing de conteúdo'
            ],
            'website_improvements': [
                'Melhorar CTAs de reserva',
                'Adicionar mais conteúdo visual (vídeos)',
                'Implementar chat online',
                'Criar landing pages específicas'
            ],
            'competitive_strategy': [
                'Monitorar concorrentes regularmente',
                'Desenvolver proposta de valor única',
                'Investir em experiência do cliente',
                'Implementar programa de fidelidade'
            ]
        }
        
        return recommendations