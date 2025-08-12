#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de inicialização rápida
Configura e inicia o projeto automaticamente
"""

import os
import subprocess
import shutil
import time
from pathlib import Path

def run_command(command, cwd=None, shell=True):
    """Executa um comando e retorna o resultado"""
    try:
        result = subprocess.run(command, shell=shell, cwd=cwd, 
                              capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_requirements():
    """Verifica se os requisitos estão instalados"""
    print("🔍 Verificando requisitos...")
    
    # Verificar Docker
    success, _, _ = run_command("docker --version")
    if not success:
        print("❌ Docker não encontrado. Instale o Docker Desktop.")
        return False
    print("✅ Docker encontrado")
    
    # Verificar Docker Compose
    success, _, _ = run_command("docker-compose --version")
    if not success:
        print("❌ Docker Compose não encontrado.")
        return False
    print("✅ Docker Compose encontrado")
    
    return True

def setup_env_file():
    """Configura o arquivo .env se não existir"""
    print("📁 Configurando arquivo .env...")
    
    env_path = Path("backend/.env")
    env_example_path = Path("backend/.env.example")
    
    if env_path.exists():
        print("✅ Arquivo .env já existe")
        return True
    
    if not env_example_path.exists():
        print("❌ Arquivo .env.example não encontrado")
        return False
    
    # Copiar .env.example para .env
    shutil.copy(env_example_path, env_path)
    print("✅ Arquivo .env criado a partir do .env.example")
    
    print("⚠️  IMPORTANTE: Configure as seguintes variáveis no backend/.env:")
    print("   - GEMINI_API_KEY (obrigatório para IA)")
    print("   - N8N_WEBHOOK_SECRET (gere uma senha segura)")
    print("   - N8N_AUTH_USER e N8N_AUTH_PASSWORD (para acessar n8n)")
    print("   - SUPABASE_URL e SUPABASE_KEY (se usar Supabase)")
    
    return True

def build_and_start():
    """Constrói e inicia os containers"""
    print("🐳 Construindo e iniciando containers...")
    
    # Parar containers existentes
    print("   Parando containers existentes...")
    run_command("docker-compose -f docker-compose-with-n8n.yml down")
    
    # Construir imagens
    print("   Construindo imagens...")
    success, stdout, stderr = run_command(
        "docker-compose -f docker-compose-with-n8n.yml build --no-cache"
    )
    
    if not success:
        print(f"❌ Erro ao construir: {stderr}")
        return False
    
    # Iniciar serviços
    print("   Iniciando serviços...")
    success, stdout, stderr = run_command(
        "docker-compose -f docker-compose-with-n8n.yml up -d"
    )
    
    if not success:
        print(f"❌ Erro ao iniciar: {stderr}")
        return False
    
    print("✅ Containers iniciados com sucesso")
    return True

def wait_for_services():
    """Aguarda os serviços ficarem prontos"""
    print("⏳ Aguardando serviços ficarem prontos...")
    
    import requests
    
    services = {
        "Backend": "http://localhost:5000/health",
        "Frontend": "http://localhost",
        "n8n": "http://localhost:5678"
    }
    
    max_attempts = 30
    for service, url in services.items():
        print(f"   Verificando {service}...")
        
        for attempt in range(max_attempts):
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"   ✅ {service} pronto")
                    break
            except:
                pass
            
            if attempt < max_attempts - 1:
                time.sleep(2)
        else:
            print(f"   ⚠️  {service} pode não estar pronto ainda")
    
    print("✅ Verificação de serviços concluída")

def show_next_steps():
    """Mostra os próximos passos"""
    print("\n🎉 SETUP CONCLUÍDO!")
    print("=" * 50)
    
    print("\n🔗 Acesse os serviços:")
    print("   Frontend: http://localhost")
    print("   Backend API: http://localhost:5000")
    print("   n8n Interface: http://localhost:5678")
    
    print("\n📋 Próximos passos:")
    print("   1. Configure as variáveis no backend/.env")
    print("   2. Importe o workflow n8n (n8n-workflow-example.json)")
    print("   3. Teste a análise básica no frontend")
    print("   4. Teste a análise com IA")
    
    print("\n🔧 Comandos úteis:")
    print("   Verificar status: python check_system.py")
    print("   Ver logs: docker-compose -f docker-compose-with-n8n.yml logs")
    print("   Parar: docker-compose -f docker-compose-with-n8n.yml down")
    print("   Reiniciar: docker-compose -f docker-compose-with-n8n.yml restart")
    
    print("\n📚 Documentação:")
    print("   Guia completo: GUIA_IMPLEMENTACAO_IA.md")
    print("   Documentação técnica: DOCUMENTACAO_TECNICA_IA.md")
    print("   README: README.md")

def main():
    print("🚀 SETUP RÁPIDO - Análise de Presença Digital com IA")
    print("=" * 60)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists("docker-compose-with-n8n.yml"):
        print("❌ Execute este script no diretório raiz do projeto")
        return
    
    # Verificar requisitos
    if not check_requirements():
        print("\n❌ Requisitos não atendidos. Instale Docker e Docker Compose.")
        return
    
    # Configurar .env
    if not setup_env_file():
        print("\n❌ Erro ao configurar arquivo .env")
        return
    
    # Perguntar se deve continuar
    print("\n⚠️  ATENÇÃO: Este script irá:")
    print("   - Parar containers existentes")
    print("   - Reconstruir todas as imagens")
    print("   - Iniciar todos os serviços")
    print("   - Isso pode levar alguns minutos")
    
    response = input("\nContinuar? (s/N): ").lower().strip()
    if response not in ['s', 'sim', 'y', 'yes']:
        print("Setup cancelado.")
        return
    
    # Construir e iniciar
    if not build_and_start():
        print("\n❌ Erro durante o build/start")
        return
    
    # Aguardar serviços
    wait_for_services()
    
    # Mostrar próximos passos
    show_next_steps()

if __name__ == "__main__":
    main()