# Configuração do Instagram Scraper
# Para reativar o scraping, mude SCRAPING_ENABLED para True

# Status do scraping do Instagram
SCRAPING_ENABLED = False

# Configurações do Selenium (quando ativado)
SELENIUM_CONFIG = {
    'command_executor': 'http://selenium:4444/wd/hub',
    'timeout': 10,
    'headless': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Dados mock para quando o scraping estiver desativado
MOCK_DATA = {
    'scraping_disabled': True,
    'message': 'Scraping do Instagram temporariamente desativado',
    'followers': None,
    'following': None,
    'posts_count': None,
    'last_post_date': None,
    'bio_complete': False,
    'profile_picture': False,
    'is_business_account': False
}
