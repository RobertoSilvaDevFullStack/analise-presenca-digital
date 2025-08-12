import streamlit as st
import requests
import json
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Análise de Presença Digital",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🚀 Análise de Presença Digital")
st.markdown("**Analise websites, presença no Google e Instagram com IA**")

# Sidebar para configurações
with st.sidebar:
    st.header("⚙️ Configurações")
    
    # URL do backend (para desenvolvimento local)
    backend_url = st.text_input(
        "URL do Backend", 
        value="http://localhost:5000",
        help="URL do seu backend Flask"
    )
    
    # Opções de análise
    st.subheader("📊 Opções de Análise")
    incluir_google = st.checkbox("Incluir análise Google", value=True)
    incluir_instagram = st.checkbox("Incluir análise Instagram", value=True)
    usar_ia = st.checkbox("Usar análise com IA", value=False)

# Formulário principal
with st.form("analise_form"):
    st.subheader("🌐 Website para Análise")
    
    website_url = st.text_input(
        "URL do Website",
        placeholder="https://exemplo.com",
        help="Digite a URL completa do website que deseja analisar"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        submit_button = st.form_submit_button("🔍 Analisar", use_container_width=True)
    
    with col2:
        if st.form_submit_button("🧹 Limpar", use_container_width=True):
            st.rerun()

# Função para fazer análise
def fazer_analise(url, backend_url, incluir_google, incluir_instagram, usar_ia):
    try:
        endpoint = "/analisar-ia" if usar_ia else "/analisar"
        
        payload = {
            "website_url": url,
            "incluir_google": incluir_google,
            "incluir_instagram": incluir_instagram
        }
        
        if usar_ia:
            payload["analysis_type"] = "comprehensive"
        
        response = requests.post(
            f"{backend_url}{endpoint}",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"Erro {response.status_code}: {response.text}"
            
    except requests.exceptions.RequestException as e:
        return None, f"Erro de conexão: {str(e)}"
    except Exception as e:
        return None, f"Erro inesperado: {str(e)}"

# Processar análise quando o botão for clicado
if submit_button and website_url:
    if not website_url.startswith(("http://", "https://")):
        st.error("❌ Por favor, insira uma URL válida (deve começar com http:// ou https://)")
    else:
        with st.spinner("🔄 Analisando... Isso pode levar alguns segundos."):
            resultado, erro = fazer_analise(
                website_url, 
                backend_url, 
                incluir_google, 
                incluir_instagram, 
                usar_ia
            )
        
        if erro:
            st.error(f"❌ {erro}")
        elif resultado:
            # Exibir resultados
            st.success("✅ Análise concluída com sucesso!")
            
            # Informações gerais
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🌐 Website", website_url)
            with col2:
                st.metric("⏰ Timestamp", resultado.get('timestamp', 'N/A'))
            with col3:
                status = "✅ Sucesso" if resultado.get('success', False) else "⚠️ Parcial"
                st.metric("📊 Status", status)
            
            # Tabs para diferentes análises
            tabs = []
            tab_names = []
            
            if 'website_analysis' in resultado:
                tab_names.append("🌐 Website")
            if 'google_results' in resultado:
                tab_names.append("🔍 Google")
            if 'instagram_data' in resultado:
                tab_names.append("📸 Instagram")
            if 'ai_analysis' in resultado or 'ai_insights' in resultado:
                tab_names.append("🤖 IA")
            
            if tab_names:
                tabs = st.tabs(tab_names)
                
                tab_index = 0
                
                # Tab Website
                if 'website_analysis' in resultado:
                    with tabs[tab_index]:
                        st.subheader("📊 Análise do Website")
                        website_data = resultado['website_analysis']
                        
                        if isinstance(website_data, dict):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write("**📋 Informações Básicas:**")
                                st.json({
                                    k: v for k, v in website_data.items() 
                                    if k in ['title', 'description', 'status_code']
                                })
                            
                            with col2:
                                st.write("**🔧 Detalhes Técnicos:**")
                                st.json({
                                    k: v for k, v in website_data.items() 
                                    if k not in ['title', 'description', 'status_code']
                                })
                        else:
                            st.json(website_data)
                    tab_index += 1
                
                # Tab Google
                if 'google_results' in resultado:
                    with tabs[tab_index]:
                        st.subheader("🔍 Resultados do Google")
                        google_data = resultado['google_results']
                        st.json(google_data)
                    tab_index += 1
                
                # Tab Instagram
                if 'instagram_data' in resultado:
                    with tabs[tab_index]:
                        st.subheader("📸 Dados do Instagram")
                        instagram_data = resultado['instagram_data']
                        st.json(instagram_data)
                    tab_index += 1
                
                # Tab IA
                if 'ai_analysis' in resultado or 'ai_insights' in resultado:
                    with tabs[tab_index]:
                        st.subheader("🤖 Análise com IA")
                        ai_content = resultado.get('ai_analysis') or resultado.get('ai_insights')
                        
                        if isinstance(ai_content, str):
                            st.markdown(ai_content)
                        else:
                            st.json(ai_content)
            
            # Botão para baixar resultados
            st.download_button(
                label="📥 Baixar Resultados (JSON)",
                data=json.dumps(resultado, indent=2, ensure_ascii=False),
                file_name=f"analise_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

elif submit_button:
    st.warning("⚠️ Por favor, insira uma URL para análise.")

# Rodapé
st.markdown("---")
st.markdown(
    "**💡 Dica:** Para melhores resultados, certifique-se de que o backend está rodando e configurado corretamente."
)

# Informações de debug (apenas em desenvolvimento)
if st.checkbox("🔧 Modo Debug"):
    st.subheader("🔧 Informações de Debug")
    st.write(f"**Backend URL:** {backend_url}")
    st.write(f"**Incluir Google:** {incluir_google}")
    st.write(f"**Incluir Instagram:** {incluir_instagram}")
    st.write(f"**Usar IA:** {usar_ia}")