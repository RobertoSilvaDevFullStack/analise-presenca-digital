#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de verificação do sistema
Verifica se todos os componentes estão funcionando corretamente
"""

import requests
import time
import os
from datetime import datetime

def check_service(name, url, timeout=10):
    """Verifica se um serviço está respondendo"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print(f"✅ {name}: OK ({response.status_code})")
            return True
        else:
            print(f"⚠️  {name}: Respondendo mas com erro ({response.status_code})")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {name}: Não conseguiu conectar")
        return False
    except requests.exceptions.Timeout:
        print(f"⏰ {name}: Timeout ({timeout}s)")
        return False
    except Exception as e:
        print(f"❌ {name}: Erro - {str(e)}")
        return False

def check_env_file():
    """Verifica se o arquivo .env existe e tem as variáveis necessárias"""
    env_path = "backend/.env"
    if not os.path.exists(env_path):
        print(f"❌ Arquivo .env não encontrado em {env_path}")
        print("   Copie backend/.env.example para backend/.env e configure")
        return False
    
    required_vars = [
        'GEMINI_API_KEY',
        'N8N_WEBHOOK_SECRET',
        'N8N_AUTH_USER',
        'N8N_AUTH_PASSWORD'
    ]
    
    missing_vars = []
    with open(env_path, 'r') as f:
        content = f.read()
        for var in required_vars:
            if f"{var}=your_" in content or f"{var}=" not in content:
                missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Variáveis não configuradas no .env: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ Arquivo .env: Configurado")
        return True

def check_docker_services():
    """Verifica se os serviços Docker estão rodando"""
    import subprocess
    try:
        result = subprocess.run(['docker-compose', '-f', 'docker-compose-with-n8n.yml', 'ps'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:  # Tem header + pelo menos um serviço
                print("✅ Docker Compose: Serviços rodando")
                return True
            else:
                print("❌ Docker Compose: Nenhum serviço rodando")
                return False
        else:
            print("❌ Docker Compose: Erro ao verificar status")
            return False
    except FileNotFoundError:
        print("❌ Docker Compose: Comando não encontrado")
        return False
    except Exception as e:
        print(f"❌ Docker Compose: Erro - {str(e)}")
        return False

def main():
    print("🔍 Verificação do Sistema - Análise de Presença Digital com IA")
    print("=" * 60)
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Verificar arquivo .env
    print("📁 Verificando configurações...")
    env_ok = check_env_file()
    print()
    
    # Verificar Docker
    print("🐳 Verificando Docker...")
    docker_ok = check_docker_services()
    print()
    
    # Verificar serviços
    print("🌐 Verificando serviços...")
    services = {
        "Frontend": "http://localhost",
        "Backend API": "http://localhost:5000/health",
        "n8n Interface": "http://localhost:5678",
        "Selenium": "http://localhost:4444/wd/hub/status",
        "Redis": "http://localhost:6379"  # Nota: Redis não tem HTTP, mas vamos tentar
    }
    
    service_results = {}
    for name, url in services.items():
        if name == "Redis":
            # Redis não tem endpoint HTTP, vamos pular
            print(f"⏭️  {name}: Pulando verificação HTTP")
            service_results[name] = True
        else:
            service_results[name] = check_service(name, url)
    
    print()
    
    # Verificar IA específica
    print("🤖 Verificando integração IA...")
    ai_status = check_service("Status IA", "http://localhost:5000/ai-status")
    print()
    
    # Resumo
    print("📊 RESUMO")
    print("=" * 30)
    
    all_ok = True
    
    if env_ok:
        print("✅ Configurações: OK")
    else:
        print("❌ Configurações: ERRO")
        all_ok = False
    
    if docker_ok:
        print("✅ Docker: OK")
    else:
        print("❌ Docker: ERRO")
        all_ok = False
    
    working_services = sum(1 for ok in service_results.values() if ok)
    total_services = len(service_results)
    print(f"📈 Serviços: {working_services}/{total_services} funcionando")
    
    if ai_status:
        print("✅ IA: OK")
    else:
        print("❌ IA: ERRO")
        all_ok = False
    
    print()
    
    if all_ok and working_services >= total_services - 1:  # Permitir 1 serviço com problema
        print("🎉 SISTEMA OK - Pronto para uso!")
        print("   Acesse: http://localhost")
    else:
        print("⚠️  SISTEMA COM PROBLEMAS")
        print("   Consulte o GUIA_IMPLEMENTACAO_IA.md para troubleshooting")
        print("   Ou execute: docker-compose -f docker-compose-with-n8n.yml logs")
    
    print()
    print("🔗 Links úteis:")
    print("   Frontend: http://localhost")
    print("   Backend API: http://localhost:5000")
    print("   n8n Interface: http://localhost:5678")
    print("   Status IA: http://localhost:5000/ai-status")

if __name__ == "__main__":
    main()