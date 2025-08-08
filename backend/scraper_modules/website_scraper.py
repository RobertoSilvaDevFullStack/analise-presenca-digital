import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import urljoin, urlparse

class WebsiteScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape(self, url):
        """Extrai informações do website"""
        try:
            # Garantir que a URL tenha protocolo
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            start_time = time.time()
            response = self.session.get(url, timeout=10)
            load_time = time.time() - start_time
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            data = {
                'url': url,
                'status_code': response.status_code,
                'load_time': round(load_time, 2),
                'has_ssl': url.startswith('https://'),
                'cms_detected': self._detect_cms(soup, response.headers),
                'developer_info': self._find_developer_info(soup),
                'title': self._get_title(soup),
                'meta_description': self._get_meta_description(soup),
                'has_analytics': self._check_analytics(soup),
                'social_links': self._find_social_links(soup),
                'page_size_kb': round(len(response.content) / 1024, 2)
            }
            
            return data
            
        except requests.RequestException as e:
            return {
                'url': url,
                'error': f'Erro ao acessar o site: {str(e)}',
                'status_code': None,
                'load_time': None,
                'has_ssl': url.startswith('https://') if url else False,
                'cms_detected': None,
                'developer_info': None
            }
    
    def _detect_cms(self, soup, headers):
        """Detecta o CMS utilizado no site"""
        cms_indicators = {
            'WordPress': [
                'wp-content', 'wp-includes', 'wordpress',
                'X-Powered-By: WordPress', 'generator.*wordpress'
            ],
            'Shopify': [
                'shopify', 'cdn.shopify.com', 'myshopify.com'
            ],
            'Magento': [
                'magento', 'mage/cookies.js', 'skin/frontend'
            ],
            'Joomla': [
                'joomla', '/media/jui/', 'option=com_'
            ],
            'Drupal': [
                'drupal', 'sites/default/files', 'misc/drupal.js'
            ],
            'Wix': [
                'wix.com', 'static.wixstatic.com'
            ],
            'Squarespace': [
                'squarespace', 'static1.squarespace.com'
            ]
        }
        
        page_content = str(soup).lower()
        headers_str = str(headers).lower()
        
        for cms, indicators in cms_indicators.items():
            for indicator in indicators:
                if indicator.lower() in page_content or indicator.lower() in headers_str:
                    return cms
        
        return None
    
    def _find_developer_info(self, soup):
        """Procura informações do desenvolvedor"""
        developer_patterns = [
            r'desenvolvido por\s*(.+?)(?:\s*\||\s*</)',
            r'developed by\s*(.+?)(?:\s*\||\s*</)',
            r'powered by\s*(.+?)(?:\s*\||\s*</)',
            r'created by\s*(.+?)(?:\s*\||\s*</)'
        ]
        
        # Buscar no rodapé
        footer = soup.find('footer')
        if footer:
            footer_text = footer.get_text()
            for pattern in developer_patterns:
                match = re.search(pattern, footer_text, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
        
        # Buscar em meta tags
        generator_tag = soup.find('meta', attrs={'name': 'generator'})
        if generator_tag:
            return generator_tag.get('content', '').strip()
        
        # Buscar links de agências/desenvolvedores
        dev_links = soup.find_all('a', href=True)
        for link in dev_links:
            href = link.get('href', '').lower()
            text = link.get_text().lower()
            if any(keyword in href or keyword in text for keyword in ['agencia', 'agency', 'desenvolvedor', 'developer', 'webdesign']):
                return link.get_text().strip()
        
        return None
    
    def _get_title(self, soup):
        """Extrai o título da página"""
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else None
    
    def _get_meta_description(self, soup):
        """Extrai a meta descrição"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        return meta_desc.get('content', '').strip() if meta_desc else None
    
    def _check_analytics(self, soup):
        """Verifica se tem Google Analytics ou similar"""
        page_content = str(soup).lower()
        analytics_indicators = [
            'google-analytics.com',
            'googletagmanager.com',
            'gtag(',
            'ga(',
            'gtm'
        ]
        return any(indicator in page_content for indicator in analytics_indicators)
    
    def _find_social_links(self, soup):
        """Encontra links para redes sociais"""
        social_platforms = {
            'facebook': ['facebook.com', 'fb.com'],
            'instagram': ['instagram.com'],
            'twitter': ['twitter.com', 'x.com'],
            'linkedin': ['linkedin.com'],
            'youtube': ['youtube.com', 'youtu.be'],
            'whatsapp': ['whatsapp.com', 'wa.me']
        }
        
        found_socials = {}
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href', '').lower()
            for platform, domains in social_platforms.items():
                if any(domain in href for domain in domains):
                    found_socials[platform] = link.get('href')
                    break
        
        return found_socials