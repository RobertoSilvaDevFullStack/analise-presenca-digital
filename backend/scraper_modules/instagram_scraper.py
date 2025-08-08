from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import time
import re
from datetime import datetime
import logging

# Importar configuração do scraping
from .instagram_config import SCRAPING_ENABLED, SELENIUM_CONFIG, MOCK_DATA

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InstagramScraper:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.setup_driver()
    
    def setup_driver(self):
        """Configura o driver do Selenium baseado na configuração"""
        
        # Verificar se o scraping está habilitado
        if not SCRAPING_ENABLED:
            logger.info("🚫 Scraping do Instagram desativado por configuração")
            self.driver = None
            self.wait = None
            return
        
        try:
            # Configurar opções do Chrome
            chrome_options = Options()
            chrome_options.add_argument('--headless' if SELENIUM_CONFIG['headless'] else '--no-headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument(f'--user-agent={SELENIUM_CONFIG["user_agent"]}')
            
            # Conectar ao container Selenium
            self.driver = webdriver.Remote(
                command_executor=SELENIUM_CONFIG['command_executor'],
                options=chrome_options
            )
            
            # Configurar WebDriverWait
            self.wait = WebDriverWait(self.driver, SELENIUM_CONFIG['timeout'])
            
            # Executar script para remover detecção de webdriver
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Driver do Selenium configurado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao configurar Selenium: {e}")
            self.driver = None
            self.wait = None
    
    def scrape(self, instagram_url):
        """Extrai informações do perfil do Instagram"""
        
        # Verificar se o scraping está habilitado
        if not SCRAPING_ENABLED:
            logger.info("🚫 Scraping do Instagram desativado por configuração")
            
            # Extrair username da URL para dados mock
            username = "usuario_exemplo"
            try:
                if 'instagram.com/' in instagram_url:
                    username = instagram_url.split('instagram.com/')[-1].strip('/')
                    if '/' in username:
                        username = username.split('/')[0]
                elif not instagram_url.startswith('http'):
                    username = instagram_url.strip("/@")
            except:
                pass
            
            # Retornar dados mock
            mock_response = MOCK_DATA.copy()
            mock_response.update({
                'url': instagram_url,
                'username': username
            })
            return mock_response
        
        # Scraping normal quando habilitado
        if not self.driver:
            return {
                'url': instagram_url,
                'error': 'Driver do Selenium não disponível',
                'followers': None,
                'following': None,
                'posts_count': None,
                'last_post_date': None,
                'bio_complete': False,
                'profile_picture': False,
                'is_business_account': False,
                'username': None
            }
        
        try:
            # Garantir que a URL esteja no formato correto
            if not instagram_url.startswith('http'):
                if 'instagram.com' not in instagram_url:
                    username = instagram_url.strip("/@")
                    instagram_url = f'https://instagram.com/{username}/'
                else:
                    instagram_url = f'https://{instagram_url}'
            
            logger.info(f"Acessando URL: {instagram_url}")
            self.driver.get(instagram_url)
            
            # Aguardar carregamento da página principal
            try:
                self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "main")))
                time.sleep(3)  # Aguardar carregamento completo
            except TimeoutException:
                logger.warning("Timeout ao aguardar carregamento da página")
            
            # Verificar se a página carregou corretamente
            if "Page Not Found" in self.driver.title or "Página não encontrada" in self.driver.page_source:
                return {
                    'url': instagram_url,
                    'error': 'Perfil não encontrado',
                    'followers': None,
                    'following': None,
                    'posts_count': None,
                    'last_post_date': None,
                    'bio_complete': False,
                    'profile_picture': False,
                    'is_business_account': False,
                    'username': None
                }
            
            data = {
                'url': instagram_url,
                'username': self._get_username(),
                'followers': self._get_followers_count(),
                'following': self._get_following_count(),
                'posts_count': self._get_posts_count(),
                'last_post_date': self._get_last_post_date(),
                'bio_complete': self._check_bio_completeness(),
                'profile_picture': self._has_profile_picture(),
                'is_business_account': self._is_business_account()
            }
            
            logger.info(f"Dados extraídos com sucesso para {data.get('username', 'usuário desconhecido')}")
            return data
            
        except Exception as e:
            logger.error(f"Erro ao extrair dados: {str(e)}")
            return {
                'url': instagram_url,
                'error': f'Erro ao extrair dados: {str(e)}',
                'followers': None,
                'following': None,
                'posts_count': None,
                'last_post_date': None,
                'bio_complete': False,
                'profile_picture': False,
                'is_business_account': False,
                'username': None
            }
    
    def close_driver(self):
        """Fecha o driver do Selenium"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Driver fechado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao fechar driver: {e}")
            finally:
                self.driver = None
                self.wait = None
    
    def _is_valid_bio(self, bio_text):
        """
        Valida se o texto parece ser uma bio válida do Instagram
        """
        if not bio_text or len(bio_text) < 5:
            return False
            
        # Bio muito longa provavelmente não é uma bio
        if len(bio_text) > 500:
            return False
            
        # Evitar textos que claramente não são bio
        avoid_bio_texts = [
            'followers', 'following', 'posts', 'reels', 'tagged',
            'follow', 'message', 'share', 'more', 'edit profile',
            'view profile', 'story highlights', 'highlights',
            'activity', 'archive', 'settings', 'switch accounts',
            'log out', 'meta', 'about', 'help', 'press', 'api',
            'jobs', 'privacy', 'terms', 'locations', 'language'
        ]
        
        bio_lower = bio_text.lower()
        for avoid_text in avoid_bio_texts:
            if avoid_text in bio_lower:
                return False
                
        # Bio deve ter pelo menos 10 caracteres para ser considerada válida
        return len(bio_text) >= 10

    def _is_valid_username(self, username):
        """
        Valida se o texto parece ser um username válido do Instagram
        """
        if not username or len(username) == 0:
            return False
            
        # Remover @ se estiver presente
        clean_username = username.lstrip('@')
        
        # Verificações básicas
        if len(clean_username) == 0 or len(clean_username) > 30:
            return False
            
        # Username não pode ter espaços ou caracteres especiais (exceto ponto e underscore)
        import re
        if not re.match(r'^[a-zA-Z0-9._]+$', clean_username):
            return False
            
        # Não pode começar ou terminar com ponto
        if clean_username.startswith('.') or clean_username.endswith('.'):
            return False
            
        # Não pode ter pontos consecutivos
        if '..' in clean_username:
            return False
            
        # Evitar textos que claramente não são usernames
        avoid_texts = [
            'followers', 'following', 'posts', 'reels', 'tagged',
            'follow', 'message', 'share', 'more', 'edit profile',
            'view profile', 'story highlights', 'highlights'
        ]
        
        if clean_username.lower() in avoid_texts:
            return False
            
        return True

    def _get_followers_count(self):
        """Extrai o número de seguidores"""
        if not self.driver:
            return None
            
        try:
            # Seletores robustos atualizados para Instagram 2025
            selectors = [
                # Seletores específicos para followers - ordem de prioridade
                "a[href*='/followers/'] span[title]",
                "a[href*='/followers/'] span:not([title])",
                "header section ul li:nth-child(2) button span[title]",
                "header section ul li:nth-child(2) a span[title]",
                "header section ul li:nth-child(2) span[title]",
                
                # Seletores alternativos com texto específico
                "span[title*='follower' i]",
                "span[title*='seguidor' i]",
                "button span[title*='follower' i]",
                "button span[title*='seguidor' i]",
                
                # Seletores por posição (estrutura padrão do Instagram)
                "header section div div ul li:nth-child(2) button span",
                "header section div div ul li:nth-child(2) a span",
                "main header section ul li:nth-child(2) span",
                
                # Seletores genéricos com validação posterior
                "ul li button span[title]",
                "ul li a span[title]",
                "header span[title]",
                
                # Fallbacks para estruturas diferentes
                "div[role='tablist'] ~ div span[title]",
                "[data-testid*='follower'] span",
                "span:contains('followers')",
                "span:contains('seguidores')"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.get_attribute('title') or element.text or ''
                        if text and ('seguidor' in text.lower() or 'follower' in text.lower() or text.replace(',', '').replace('.', '').isdigit()):
                            followers = self._parse_count(text)
                            if followers is not None:
                                logger.debug(f"Seguidores encontrados: {followers}")
                                return followers
                except Exception as e:
                    logger.debug(f"Erro com seletor {selector}: {e}")
                    continue
            
            logger.warning("Não foi possível extrair o número de seguidores")
            return None
        except Exception as e:
            logger.error(f"Erro ao extrair seguidores: {e}")
            return None
    
    def _get_following_count(self):
        """Extrai o número de pessoas seguindo"""
        if not self.driver:
            return None
            
        try:
            # Seletores robustos atualizados para Instagram 2025
            selectors = [
                # Seletores específicos para following - ordem de prioridade
                "a[href*='/following/'] span[title]",
                "a[href*='/following/'] span:not([title])",
                "header section ul li:nth-child(3) button span[title]",
                "header section ul li:nth-child(3) a span[title]",
                "header section ul li:nth-child(3) span[title]",
                
                # Seletores alternativos com texto específico
                "span[title*='following' i]",
                "span[title*='seguindo' i]",
                "button span[title*='following' i]",
                "button span[title*='seguindo' i]",
                
                # Seletores por posição (estrutura padrão do Instagram)
                "header section div div ul li:nth-child(3) button span",
                "header section div div ul li:nth-child(3) a span",
                "main header section ul li:nth-child(3) span",
                
                # Seletores genéricos com validação posterior
                "ul li:nth-child(3) button span",
                "ul li:nth-child(3) a span",
                
                # Fallbacks para estruturas diferentes
                "[data-testid*='following'] span",
                "span:contains('following')",
                "span:contains('seguindo')"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.get_attribute('title') or element.text or ''
                        if text and ('seguindo' in text.lower() or 'following' in text.lower() or text.replace(',', '').replace('.', '').isdigit()):
                            following = self._parse_count(text)
                            if following is not None:
                                logger.debug(f"Seguindo encontrados: {following}")
                                return following
                except Exception as e:
                    logger.debug(f"Erro com seletor {selector}: {e}")
                    continue
            
            logger.warning("Não foi possível extrair o número de seguindo")
            return None
        except Exception as e:
            logger.error(f"Erro ao extrair seguindo: {e}")
            return None
    
    def _get_posts_count(self):
        """Extrai o número de posts"""
        if not self.driver:
            return None
            
        try:
            # Seletores robustos atualizados para Instagram 2025
            selectors = [
                # Seletores específicos para posts - ordem de prioridade
                "header section ul li:first-child button span[title]",
                "header section ul li:first-child a span[title]",
                "header section ul li:first-child span[title]",
                
                # Seletores alternativos com texto específico
                "span[title*='post' i]",
                "span[title*='publicaç' i]",
                "span[title*='publication' i]",
                "button span[title*='post' i]",
                "button span[title*='publicaç' i]",
                
                # Seletores por posição (estrutura padrão do Instagram)
                "header section div div ul li:first-child button span",
                "header section div div ul li:first-child a span",
                "main header section ul li:first-child span",
                
                # Seletores genéricos com validação posterior
                "ul li:first-child button span[title]",
                "ul li:first-child a span[title]",
                "ul li:first-child span[title]",
                
                # Fallbacks para estruturas diferentes
                "[data-testid*='post'] span",
                "span:contains('posts')",
                "span:contains('publicações')",
                
                # Seletores alternativos para layouts diferentes
                "div[role='button'] span[title*='post' i]",
                "article span[title*='post' i]"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.get_attribute('title') or element.text or ''
                        if text and ('post' in text.lower() or 'publicaç' in text.lower() or text.replace(',', '').replace('.', '').isdigit()):
                            posts = self._parse_count(text)
                            if posts is not None:
                                logger.debug(f"Posts encontrados: {posts}")
                                return posts
                except Exception as e:
                    logger.debug(f"Erro com seletor {selector}: {e}")
                    continue
            
            logger.warning("Não foi possível extrair o número de posts")
            return None
        except Exception as e:
            logger.error(f"Erro ao extrair posts: {e}")
            return None
    
    def _get_last_post_date(self):
        """Tenta extrair a data da última postagem de forma mais robusta"""
        if not self.driver:
            return None
            
        try:
            # Primeiro verificar se há posts
            post_selectors = [
                "article div div div div a",
                "article a[href*='/p/']",
                "div[role='tabpanel'] a[href*='/p/']",
                "main article a"
            ]
            
            first_post = None
            for selector in post_selectors:
                try:
                    posts = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if posts:
                        first_post = posts[0]
                        break
                except:
                    continue
            
            if not first_post:
                logger.warning("Nenhum post encontrado")
                return None
            
            # Tentar obter a data através do atributo href primeiro
            try:
                href = first_post.get_attribute('href')
                if href and '/p/' in href:
                    # Extrair código do post da URL
                    post_code = href.split('/p/')[-1].rstrip('/')
                    logger.debug(f"Código do post encontrado: {post_code}")
            except:
                pass
            
            # Tentar clicar no post para ver detalhes
            try:
                self.driver.execute_script("arguments[0].click();", first_post)
                time.sleep(2)
                
                # Procurar por elementos de tempo no modal
                time_selectors = [
                    "time[datetime]",
                    "time",
                    "span[title*='UTC']",
                    "a time[datetime]"
                ]
                
                for selector in time_selectors:
                    try:
                        time_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for time_elem in time_elements:
                            datetime_attr = time_elem.get_attribute('datetime')
                            if datetime_attr:
                                # Converter para formato de data
                                try:
                                    post_date = datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
                                    formatted_date = post_date.strftime('%Y-%m-%d')
                                    logger.debug(f"Data da última postagem: {formatted_date}")
                                    
                                    # Fechar modal
                                    self.driver.execute_script("window.history.back();")
                                    time.sleep(1)
                                    
                                    return formatted_date
                                except ValueError:
                                    continue
                    except:
                        continue
                
                # Se não encontrou via modal, fechar e continuar
                self.driver.execute_script("window.history.back();")
                time.sleep(1)
                
            except Exception as e:
                logger.debug(f"Erro ao abrir modal do post: {e}")
            
            logger.warning("Não foi possível extrair a data da última postagem")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao extrair data da última postagem: {e}")
            return None
    
    def _check_bio_completeness(self):
        """Verifica se a bio está completa"""
        if not self.driver:
            return False
            
        try:
            bio_selectors = [
                # Seletores específicos para bio 2025
                "header section div[dir='auto'] span",
                "header section div span[dir='auto']",
                "div[data-testid='user-description'] span",
                "header div[role='main'] div span",
                "section div div span[style*='word-wrap']",
                
                # Seletores alternativos mais específicos
                "header section div:nth-child(2) span",
                "header div[style*='flex-direction'] span",
                "article header section div span",
                
                # Seletores gerais de fallback
                "header section div span",
                "header div span",
                "h1 + div span",
                "section span",
                "div[style*='word-wrap'] span",
                
                # Seletores por posição
                "header section > div:nth-child(2) span",
                "header > div > div > div:nth-child(2) span"
            ]
            
            for selector in bio_selectors:
                try:
                    bio_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for bio_element in bio_elements:
                        bio_text = bio_element.text.strip() if bio_element else ""
                        
                        # Validação mais rigorosa para bio
                        if self._is_valid_bio(bio_text):
                            logger.debug(f"Bio encontrada: {bio_text[:50]}...")
                            return True
                except:
                    continue
            
            logger.debug("Bio não encontrada ou muito curta")
            return False
        except Exception as e:
            logger.error(f"Erro ao verificar bio: {e}")
            return False
    
    def _has_profile_picture(self):
        """Verifica se tem foto de perfil personalizada"""
        if not self.driver:
            return False
            
        try:
            profile_img_selectors = [
                # Seletores específicos para foto de perfil 2025
                "header img[data-testid='user-avatar']",
                "header button img[alt*='foto']",
                "header div[role='button'] img",
                "header span img[crossorigin='anonymous']",
                "article header img[style*='border-radius']",
                
                # Seletores alternativos mais específicos
                "header img[alt*='foto de perfil']",
                "header img[alt*='profile picture']",
                "header img[alt*='foto']",
                "header img[alt*='profile']", 
                "header img[alt*='picture']",
                
                # Seletores por estrutura
                "header > div img:first-child",
                "header section img:first-child",
                "header div:first-child img",
                
                # Seletores gerais de fallback
                "header img",
                "canvas + img",
                "div[role='button'] img"
            ]
            
            for selector in profile_img_selectors:
                try:
                    profile_imgs = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for profile_img in profile_imgs:
                        src = profile_img.get_attribute('src')
                        alt = profile_img.get_attribute('alt') or ''
                        
                        # Verificar se não é a imagem padrão
                        if src and not any(default in src.lower() for default in ['default', 'anonymous', 'avatar']):
                            # Verificar tamanho da imagem (profile pics são geralmente maiores que 44px)
                            size = profile_img.size
                            if size and size.get('width', 0) > 44:
                                logger.debug("Foto de perfil personalizada encontrada")
                                return True
                except:
                    continue
            
            logger.debug("Foto de perfil padrão ou não encontrada")
            return False
        except Exception as e:
            logger.error(f"Erro ao verificar foto de perfil: {e}")
            return False
    
    def _is_business_account(self):
        """Verifica se é conta comercial"""
        if not self.driver:
            return False
            
        try:
            page_source = self.driver.page_source.lower()
            
            # Indicadores mais específicos para conta comercial
            business_indicators = [
                'conta comercial',
                'business account', 
                'entrar em contato',
                'contact',
                'categoria',
                'category',
                'website',
                'site',
                'email',
                'telefone',
                'phone',
                'endereço',
                'address'
            ]
            
            # Contar quantos indicadores foram encontrados
            found_indicators = sum(1 for indicator in business_indicators if indicator in page_source)
            
            # Também verificar por elementos específicos de conta comercial
            business_elements = [
                "button[aria-label*='Contact']",
                "button[aria-label*='Contato']",
                "a[href*='mailto:']",
                "a[href*='tel:']",
                "span[title*='Category']",
                "span[title*='Categoria']"
            ]
            
            for selector in business_elements:
                try:
                    if self.driver.find_elements(By.CSS_SELECTOR, selector):
                        found_indicators += 1
                except:
                    continue
            
            # Considerar conta comercial se encontrar 2 ou mais indicadores
            is_business = found_indicators >= 2
            logger.debug(f"Conta comercial: {is_business} (indicadores: {found_indicators})")
            return is_business
            
        except Exception as e:
            logger.error(f"Erro ao verificar conta comercial: {e}")
            return False
    
    def _get_username(self):
        """Extrai o nome de usuário"""
        if not self.driver:
            return None
            
        try:
            # Seletores robustos para username - Instagram 2025
            username_selectors = [
                # Seletores específicos para nome de usuário
                "header section div h2",
                "header section div h1", 
                "main header section div h2",
                "main header section div h1",
                
                # Seletores alternativos
                "header h1:not([title])",
                "header h2:not([title])",
                "[data-testid='user-name']",
                "[data-testid='username']",
                
                # Seletores genéricos com validação
                "header section span:first-child",
                "header div span:first-of-type",
                "h1[dir='auto']",
                "h2[dir='auto']",
                
                # Fallbacks
                "header span[title]:not([title*='follower']):not([title*='seguidor']):not([title*='post']):not([title*='following']):not([title*='seguindo'])",
                "header section div:first-child span"
            ]
            
            for selector in username_selectors:
                try:
                    username_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in username_elements:
                        text = element.text.strip()
                        
                        # Validação mais rigorosa para username do Instagram
                        if text and self._is_valid_username(text):
                            logger.debug(f"Username encontrado: {text}")
                            return text
                except:
                    continue
            
            # Fallback: tentar extrair da URL atual
            try:
                current_url = self.driver.current_url
                if 'instagram.com/' in current_url:
                    username = current_url.split('instagram.com/')[-1].split('/')[0]
                    if username and username != 'www':
                        logger.debug(f"Username extraído da URL: {username}")
                        return username
            except:
                pass
                
            logger.warning("Username não encontrado")
            return None
        except Exception as e:
            logger.error(f"Erro ao extrair username: {e}")
            return None
    
    def _parse_count(self, text):
        """Converte texto de contagem em número de forma mais robusta"""
        if not text:
            return None
        
        # Normalizar texto
        text = str(text).lower().strip()
        
        # Remover caracteres especiais mas manter pontos e vírgulas para números
        text = re.sub(r'[^\w\s.,]', '', text)
        
        try:
            # Procurar por padrões de números com sufixos
            # Padrão para milhões
            if any(suffix in text for suffix in ['m', 'mi', 'milhão', 'milhões', 'million']):
                number_match = re.search(r'(\d+(?:[.,]\d+)?)', text)
                if number_match:
                    number = float(number_match.group(1).replace(',', '.'))
                    return int(number * 1000000)
            
            # Padrão para milhares
            elif any(suffix in text for suffix in ['k', 'mil', 'thousand']):
                number_match = re.search(r'(\d+(?:[.,]\d+)?)', text)
                if number_match:
                    number = float(number_match.group(1).replace(',', '.'))
                    return int(number * 1000)
            
            # Apenas números (com possíveis separadores de milhares)
            else:
                # Remover espaços e manter apenas dígitos, pontos e vírgulas
                clean_text = re.sub(r'[^\d.,]', '', text)
                
                if not clean_text:
                    return None
                
                # Se contém vírgula seguida de 3 dígitos, tratar como separador de milhares
                if re.match(r'\d{1,3}(,\d{3})+$', clean_text):
                    clean_text = clean_text.replace(',', '')
                # Se contém ponto seguido de 3 dígitos, tratar como separador de milhares
                elif re.match(r'\d{1,3}(\.\d{3})+$', clean_text):
                    clean_text = clean_text.replace('.', '')
                
                # Tentar converter para inteiro
                if clean_text.isdigit():
                    return int(clean_text)
                
                # Tentar converter removendo pontos/vírgulas finais
                clean_text = clean_text.rstrip('.,')
                if clean_text.isdigit():
                    return int(clean_text)
        
        except (ValueError, AttributeError) as e:
            logger.debug(f"Erro ao converter '{text}' para número: {e}")
        
        return None