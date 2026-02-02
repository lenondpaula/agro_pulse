"""
AgroPulse Media Watch - Main Application
Dashboard de Monitoramento de Mídia (Clipagem e Rádio Escuta)
Design: High Contrast Dark Mode / Grey / White
"""

import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
import sys
import os

# Adiciona o diretório src ao path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from media_engine import (
    get_web_news,
    simulate_radio_listening,
    simulate_social_buzz,
    get_sentiment_summary
)

# ============================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================
st.set_page_config(
    page_title="AgroPulse Media Watch",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None
)

# ============================================
# TEXTOS INTERNACIONALIZADOS
# ============================================
TRANSLATIONS = {
    'pt-br': {
        'title': '📡 AgroPulse Media Watch',
        'subtitle': 'Monitoramento de Mídia em Tempo Real | Agro en Punta 2026',
        'web_news': 'Web News (24h)',
        'radio_citations': 'Citações em Rádio (Ao Vivo)',
        'global_sentiment': 'Sentimento Global',
        'positive': 'Positivo',
        'neutral': 'Neutro',
        'attention': 'Atenção',
        'radio_feed': '🎙️ Rádio Escuta — Feed Ao Vivo',
        'mentions_volume': '📈 Volume de Menções por Hora',
        'web_news_title': '🌐 Notícias Web — Google News',
        'no_news': 'Nenhuma notícia encontrada no momento.',
        'last_mention': 'ÚLTIMA MENÇÃO',
        'coverage': 'Cobertura: Agro en Punta 2026 | Uruguai & Brasil',
        'footer_title': 'AgroPulse Media Watch | Monitoramento de Mídia em Tempo Real',
        'footer_subtitle': 'Cobertura: Agro en Punta 2026 | Dados atualizados a cada 5 minutos',
        'hour': 'Hora',
        'vehicle': 'Veículo',
        'title_col': 'Título',
        'platform': 'Plataforma',
        'mentions': 'Menções',
        'language': 'Idioma',
        'theme': 'Tema Visual',
    },
    'es-uy': {
        'title': '📡 AgroPulse Media Watch',
        'subtitle': 'Monitoreo de Medios en Tiempo Real | Agro en Punta 2026',
        'web_news': 'Noticias Web (24h)',
        'radio_citations': 'Menciones en Radio (En Vivo)',
        'global_sentiment': 'Sentimiento Global',
        'positive': 'Positivo',
        'neutral': 'Neutro',
        'attention': 'Atención',
        'radio_feed': '🎙️ Escucha de Radio — Feed En Vivo',
        'mentions_volume': '📈 Volumen de Menciones por Hora',
        'web_news_title': '🌐 Noticias Web — Google News',
        'no_news': 'No se encontraron noticias en este momento.',
        'last_mention': 'ÚLTIMA MENCIÓN',
        'coverage': 'Cobertura: Agro en Punta 2026 | Uruguay & Brasil',
        'footer_title': 'AgroPulse Media Watch | Monitoreo de Medios en Tiempo Real',
        'footer_subtitle': 'Cobertura: Agro en Punta 2026 | Datos actualizados cada 5 minutos',
        'hour': 'Hora',
        'vehicle': 'Medio',
        'title_col': 'Título',
        'platform': 'Plataforma',
        'mentions': 'Menciones',
        'language': 'Idioma',
        'theme': 'Tema Visual',
    }
}

# ============================================
# TEMAS VISUAIS
# ============================================
THEMES = {
    'dark': {
        'name': '🌙 Dark',
        'bg_primary': '#0E1117',
        'bg_secondary': '#1A1F2E',
        'bg_card': '#151922',
        'accent': '#00FF88',
        'text_primary': '#FAFAFA',
        'text_secondary': '#A0AEC0',
        'text_muted': '#718096',
        'border': '#2D3748',
        'negative': '#FF4444',
        'chart_bg': '#0E1117',
    },
    'grey': {
        'name': '🌫️ Grey',
        'bg_primary': '#2D3748',
        'bg_secondary': '#4A5568',
        'bg_card': '#3D4A5C',
        'accent': '#48BB78',
        'text_primary': '#F7FAFC',
        'text_secondary': '#CBD5E0',
        'text_muted': '#A0AEC0',
        'border': '#5A6A7A',
        'negative': '#FC8181',
        'chart_bg': '#2D3748',
    },
    'white': {
        'name': '☀️ White',
        'bg_primary': '#FFFFFF',
        'bg_secondary': '#F7FAFC',
        'bg_card': '#EDF2F7',
        'accent': '#38A169',
        'text_primary': '#1A202C',
        'text_secondary': '#4A5568',
        'text_muted': '#718096',
        'border': '#E2E8F0',
        'negative': '#E53E3E',
        'chart_bg': '#FFFFFF',
    }
}

# ============================================
# INICIALIZAÇÃO DO SESSION STATE
# ============================================
if 'language' not in st.session_state:
    st.session_state.language = 'pt-br'
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

# ============================================
# FUNÇÕES DE CALLBACK PARA TOGGLES
# ============================================
def toggle_language():
    """Alterna entre PT-BR e ES-UY."""
    if st.session_state.language == 'pt-br':
        st.session_state.language = 'es-uy'
    else:
        st.session_state.language = 'pt-br'

def cycle_theme():
    """Cicla entre os temas: dark → grey → white → dark."""
    theme_order = ['dark', 'grey', 'white']
    current_idx = theme_order.index(st.session_state.theme)
    next_idx = (current_idx + 1) % len(theme_order)
    st.session_state.theme = theme_order[next_idx]

# Obtém textos e tema atual
t = TRANSLATIONS[st.session_state.language]
theme = THEMES[st.session_state.theme]

# ============================================
# CSS CUSTOMIZADO - DINÂMICO POR TEMA
# ============================================
st.markdown(f"""
<style>
    /* Remove padding superior e configura fundo */
    .stApp {{
        background-color: {theme['bg_primary']};
    }}
    
    .block-container {{
        padding-top: 3.5rem !important;
        padding-bottom: 1rem !important;
    }}
    
    /* Esconde sidebar completamente */
    [data-testid="stSidebar"] {{
        display: none !important;
    }}
    
    [data-testid="stSidebarCollapsedControl"] {{
        display: none !important;
    }}
    
    button[kind="header"] {{
        display: none !important;
    }}
    
    /* Header do Streamlit - ajusta altura para não sobrepor */
    header[data-testid="stHeader"] {{
        background-color: {theme['bg_primary']};
        height: 3rem;
    }}
    
    /* Ticker de rolagem */
    .ticker-wrapper {{
        background: linear-gradient(90deg, {theme['bg_secondary']} 0%, {theme['bg_primary']} 50%, {theme['bg_secondary']} 100%);
        border-bottom: 2px solid {theme['accent']};
        padding: 10px 0;
        margin-bottom: 20px;
        margin-top: 10px;
        overflow: hidden;
    }}
    
    .ticker-content {{
        color: {theme['accent']};
        font-size: 1.1rem;
        font-weight: 600;
        white-space: nowrap;
        animation: scroll-left 20s linear infinite;
    }}
    
    @keyframes scroll-left {{
        0% {{ transform: translateX(100%); }}
        100% {{ transform: translateX(-100%); }}
    }}
    
    /* Cards de KPI */
    .kpi-card {{
        background: linear-gradient(135deg, {theme['bg_secondary']} 0%, {theme['bg_card']} 100%);
        border: 1px solid {theme['border']};
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        transition: border-color 0.3s;
    }}
    
    .kpi-card:hover {{
        border-color: {theme['accent']};
    }}
    
    .kpi-value {{
        color: {theme['accent']};
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }}
    
    .kpi-label {{
        color: {theme['text_secondary']};
        font-size: 0.9rem;
        margin-top: 5px;
    }}
    
    /* Timeline de Rádio */
    .radio-card {{
        background: {theme['bg_secondary']};
        border-left: 4px solid {theme['accent']};
        border-radius: 0 8px 8px 0;
        padding: 12px 15px;
        margin-bottom: 10px;
        transition: transform 0.2s;
    }}
    
    .radio-card:hover {{
        transform: translateX(5px);
    }}
    
    .radio-card.negativo, .radio-card.negative {{
        border-left-color: {theme['negative']};
        background: linear-gradient(90deg, rgba(255,68,68,0.15) 0%, {theme['bg_secondary']} 30%);
    }}
    
    .radio-card.positivo, .radio-card.positive {{
        border-left-color: {theme['accent']};
    }}
    
    .radio-card.neutro, .radio-card.neutral {{
        border-left-color: {theme['text_secondary']};
    }}
    
    .radio-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }}
    
    .radio-station {{
        color: {theme['accent']};
        font-weight: 600;
        font-size: 0.95rem;
    }}
    
    .radio-time {{
        color: {theme['text_muted']};
        font-size: 0.8rem;
    }}
    
    .radio-text {{
        color: {theme['text_primary']};
        font-size: 0.9rem;
        line-height: 1.4;
        font-style: italic;
    }}
    
    /* Seções */
    .section-title {{
        color: {theme['text_primary']};
        font-size: 1.2rem;
        font-weight: 600;
        border-bottom: 2px solid {theme['accent']};
        padding-bottom: 8px;
        margin-bottom: 15px;
    }}
    
    /* Tabela de notícias */
    .news-table {{
        background: {theme['bg_secondary']};
        border-radius: 8px;
        padding: 10px;
        width: 100%;
        border-collapse: collapse;
    }}
    
    .news-table th {{
        background: {theme['bg_card']};
        color: {theme['text_primary']};
        padding: 12px;
        text-align: left;
        border-bottom: 2px solid {theme['accent']};
    }}
    
    .news-table td {{
        padding: 10px 12px;
        border-bottom: 1px solid {theme['border']};
        color: {theme['text_primary']};
    }}
    
    .news-table tr:hover {{
        background: {theme['bg_card']};
    }}
    
    /* Links clicáveis */
    a {{
        color: {theme['accent']} !important;
        text-decoration: none !important;
    }}
    
    a:hover {{
        text-decoration: underline !important;
    }}
    
    /* Footer */
    .footer-container {{
        text-align: center;
        color: {theme['text_muted']};
        font-size: 0.85rem;
        border-top: 1px solid {theme['border']};
        padding-top: 20px;
        margin-top: 30px;
    }}
    
    .footer-title {{
        color: {theme['accent']};
        font-weight: 700;
        font-size: 1rem;
        margin-bottom: 5px;
    }}
    
    .footer-contact {{
        margin: 15px 0;
    }}
    
    .footer-contact a {{
        margin: 0 10px;
        color: {theme['accent']} !important;
    }}
    
    .footer-copyright {{
        margin-top: 15px;
        padding-top: 15px;
        border-top: 1px solid {theme['border']};
        color: {theme['text_muted']};
    }}
</style>
""", unsafe_allow_html=True)

# ============================================
# CARREGA DADOS
# ============================================
@st.cache_data(ttl=300)  # Cache de 5 minutos
def load_data(lang='pt-br'):
    """Carrega todos os dados das fontes baseado no idioma selecionado."""
    web_news = get_web_news(lang)
    radio_data = simulate_radio_listening(lang)
    social_buzz = simulate_social_buzz()
    sentiment = get_sentiment_summary(radio_data)
    return web_news, radio_data, social_buzz, sentiment

# Carrega dados com o idioma selecionado
current_lang = st.session_state.language
web_news_df, radio_df, social_df, sentiment_summary = load_data(current_lang)

# ============================================
# TICKER SUPERIOR - ÚLTIMA MENÇÃO EM RÁDIO
# ============================================
if not radio_df.empty:
    latest_mention = radio_df.iloc[0]
    ticker_text = f"🎙️ {t['last_mention']}: [{latest_mention['Emissora']}] {latest_mention['Transcrição']} — {latest_mention['Timestamp']}"
else:
    ticker_text = f"🎙️ AGROPULSE MEDIA WATCH — {t['coverage']}"

st.markdown(f"""
<div class="ticker-wrapper">
    <div class="ticker-content">
        {ticker_text} &nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp; 
        📊 {t['coverage']} &nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp;
        {ticker_text}
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================
# BARRA DE CONTROLES NO TOPO (UX: Toggle Switches)
# ============================================
# Labels dinâmicos baseados no estado atual
lang_label = "🇧🇷 PT" if st.session_state.language == 'pt-br' else "🇺🇾 ES"
theme_icon = {'dark': '🌙', 'grey': '🌫️', 'white': '☀️'}[st.session_state.theme]
theme_label = theme_icon

# Container com CSS para alinhar à direita
st.markdown(f"""
<style>
    .top-controls {{
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 8px;
        padding: 0 0 15px 0;
        margin-top: -10px;
    }}
    .control-btn {{
        background: {theme['bg_secondary']};
        border: 1px solid {theme['border']};
        border-radius: 20px;
        padding: 6px 14px;
        color: {theme['text_primary']};
        font-size: 0.85rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }}
    .control-btn:hover {{
        background: {theme['accent']};
        color: {theme['bg_primary']};
        transform: scale(1.05);
    }}
    /* Esconde labels dos botões Streamlit */
    .stButton > button {{
        background: {theme['bg_secondary']} !important;
        border: 1px solid {theme['border']} !important;
        border-radius: 20px !important;
        color: {theme['text_primary']} !important;
        font-weight: 500 !important;
        padding: 0.4rem 1rem !important;
        transition: all 0.2s ease !important;
    }}
    .stButton > button:hover {{
        background: {theme['accent']} !important;
        color: {theme['bg_primary']} !important;
        border-color: {theme['accent']} !important;
    }}
    .stButton > button:focus {{
        box-shadow: none !important;
    }}
    div[data-testid="stHorizontalBlock"] > div:last-child {{
        display: flex;
        justify-content: flex-end;
    }}
</style>
""", unsafe_allow_html=True)

# Botões de controle alinhados à direita
col_spacer, col_lang, col_theme = st.columns([8, 1, 1])

with col_lang:
    if st.button(lang_label, key="lang_toggle", help="Alternar idioma / Cambiar idioma", use_container_width=True):
        toggle_language()
        st.rerun()

with col_theme:
    if st.button(theme_label, key="theme_toggle", help="Alternar tema / Cambiar tema", use_container_width=True):
        cycle_theme()
        st.rerun()

# ============================================
# TÍTULO
# ============================================
st.markdown(f"""
<h1 style="color: {theme['accent']}; text-align: center; margin: 0; font-size: 1.8rem;">
    {t['title']}
</h1>
<p style="color: {theme['text_muted']}; text-align: center; margin-top: 5px; font-size: 0.9rem;">
    {t['subtitle']}
</p>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================
# KPIs - MÉTRICAS PRINCIPAIS
# ============================================
kpi_cols = st.columns(3)

with kpi_cols[0]:
    st.markdown(f"""
    <div class="kpi-card">
        <p class="kpi-value">🌐 {len(web_news_df)}</p>
        <p class="kpi-label">{t['web_news']}</p>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[1]:
    st.markdown(f"""
    <div class="kpi-card">
        <p class="kpi-value">📻 {len(radio_df)}</p>
        <p class="kpi-label">{t['radio_citations']}</p>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[2]:
    # Calcula sentimento global
    total = sum(sentiment_summary.values())
    if total > 0:
        positivo_pct = (sentiment_summary['Positivo'] / total) * 100
        if positivo_pct >= 60:
            sentiment_icon = "🟢"
            sentiment_text = f"{positivo_pct:.0f}% {t['positive']}"
        elif positivo_pct >= 40:
            sentiment_icon = "⚪"
            sentiment_text = t['neutral']
        else:
            sentiment_icon = "🔴"
            sentiment_text = t['attention']
    else:
        sentiment_icon = "⚪"
        sentiment_text = "N/A"
    
    st.markdown(f"""
    <div class="kpi-card">
        <p class="kpi-value">{sentiment_icon}</p>
        <p class="kpi-label">{t['global_sentiment']}: {sentiment_text}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================
# DIVISÃO PRINCIPAL (30% / 70%)
# ============================================
col_radio, col_web = st.columns([0.30, 0.70])

# --------------------------------------------
# COLUNA ESQUERDA - RÁDIO ESCUTA (30%)
# --------------------------------------------
with col_radio:
    st.markdown(f'<p class="section-title">{t["radio_feed"]}</p>', unsafe_allow_html=True)
    
    # Container com scroll para o feed
    radio_container = st.container(height=500)
    
    with radio_container:
        for _, row in radio_df.iterrows():
            # Define classe CSS baseada no sentimento
            sentiment_class = row['Sentimento'].lower()
            
            # Ícone baseado no sentimento
            if row['Sentimento'] == 'Positivo':
                sent_icon = "🟢"
            elif row['Sentimento'] == 'Negativo':
                sent_icon = "🔴"
            else:
                sent_icon = "⚪"
            
            st.markdown(f"""
            <div class="radio-card {sentiment_class}">
                <div class="radio-header">
                    <span class="radio-station">🎙️ {row['Emissora']}</span>
                    <span class="radio-time">{row['Timestamp']} {sent_icon}</span>
                </div>
                <p class="radio-text">"{row['Transcrição']}"</p>
            </div>
            """, unsafe_allow_html=True)

# --------------------------------------------
# COLUNA DIREITA - WEB & ANÁLISE (70%)
# --------------------------------------------
with col_web:
    # TOPO: Gráfico de Volume de Menções nas Redes Sociais
    st.markdown(f'<p class="section-title">{t["mentions_volume"]}</p>', unsafe_allow_html=True)
    
    # Prepara dados para o gráfico - usando as novas redes sociais
    redes_sociais = ['X', 'Instagram', 'Facebook', 'Threads', 'LinkedIn', 'TikTok']
    chart_data = social_df[['Hora'] + redes_sociais].copy()
    chart_data = chart_data.melt(id_vars=['Hora'], var_name='Plataforma', value_name='Menções')
    
    # Cores para cada rede social
    social_colors = {
        'dark': ['#00FF88', '#E040FB', '#1877F2', '#000000', '#0A66C2', '#FF0050'],
        'grey': ['#48BB78', '#D53F8C', '#4267B2', '#1A1A1A', '#0077B5', '#EE1D52'],
        'white': ['#38A169', '#B83280', '#1877F2', '#000000', '#0A66C2', '#FF0050']
    }
    colors = social_colors.get(st.session_state.theme, social_colors['dark'])
    
    # Cria gráfico Altair com barras empilhadas
    chart = alt.Chart(chart_data).mark_bar(
        opacity=0.85
    ).encode(
        x=alt.X('Hora:N', title=t['hour'], axis=alt.Axis(labelAngle=-45, labelColor=theme['text_secondary'], titleColor=theme['text_primary'])),
        y=alt.Y('sum(Menções):Q', title=t['mentions'], axis=alt.Axis(labelColor=theme['text_secondary'], titleColor=theme['text_primary'])),
        color=alt.Color('Plataforma:N', 
                       scale=alt.Scale(domain=redes_sociais, range=colors),
                       legend=alt.Legend(title=t['platform'], labelColor=theme['text_primary'], titleColor=theme['text_primary'])),
        tooltip=['Hora', 'Plataforma', 'Menções']
    ).properties(
        height=220
    ).configure(
        background=theme['chart_bg']
    ).configure_view(
        strokeWidth=0
    )
    
    st.altair_chart(chart, use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # BAIXO: Tabela de Notícias COM ABAS
    st.markdown(f'<p class="section-title">{t["web_news_title"]}</p>', unsafe_allow_html=True)
    
    # Textos das abas por idioma
    tab_agro_punta = "🎯 Agro en Punta" if st.session_state.language == 'pt-br' else "🎯 Agro en Punta"
    tab_outros = "📰 Outras Notícias" if st.session_state.language == 'pt-br' else "📰 Otras Noticias"
    
    # Cria as abas
    tab1, tab2 = st.tabs([tab_agro_punta, tab_outros])
    
    # Função para criar link clicável
    def make_link(row):
        link = row.get('Link', '')
        title = row.get('Título', 'Sem título')
        
        # Verifica se é um link válido
        if link and link != '#' and not link.startswith('https://exemplo.com'):
            return f'<a href="{link}" target="_blank">{title}</a>'
        else:
            return title
    
    # Formata DataFrame para exibição
    if not web_news_df.empty:
        # Verifica se tem coluna Categoria (dados simulados) ou não (GoogleNews)
        has_categoria = 'Categoria' in web_news_df.columns
        
        if has_categoria:
            # Separa as notícias por categoria
            df_agro_punta = web_news_df[web_news_df['Categoria'] == 'Agro en Punta'].copy()
            df_outros = web_news_df[web_news_df['Categoria'] != 'Agro en Punta'].copy()
        else:
            # Filtra por palavras-chave no título
            mask_agro = web_news_df['Título'].str.contains('Agro en Punta|Punta del Este|evento em Punta', case=False, na=False)
            df_agro_punta = web_news_df[mask_agro].copy()
            df_outros = web_news_df[~mask_agro].copy()
        
        # Aba 1: Agro en Punta
        with tab1:
            if not df_agro_punta.empty:
                display_df = df_agro_punta.copy()
                display_df['Título'] = display_df.apply(make_link, axis=1)
                display_df = display_df[['Hora', 'Veículo', 'Título']]
                display_df.columns = [t['hour'], t['vehicle'], t['title_col']]
                st.markdown(
                    display_df.to_html(escape=False, index=False, classes='news-table'),
                    unsafe_allow_html=True
                )
            else:
                no_news_agro = "Nenhuma notícia sobre Agro en Punta no momento." if st.session_state.language == 'pt-br' else "No hay noticias sobre Agro en Punta en este momento."
                st.info(no_news_agro)
        
        # Aba 2: Outras Notícias
        with tab2:
            if not df_outros.empty:
                display_df = df_outros.copy()
                display_df['Título'] = display_df.apply(make_link, axis=1)
                display_df = display_df[['Hora', 'Veículo', 'Título']]
                display_df.columns = [t['hour'], t['vehicle'], t['title_col']]
                st.markdown(
                    display_df.to_html(escape=False, index=False, classes='news-table'),
                    unsafe_allow_html=True
                )
            else:
                no_news_other = "Nenhuma outra notícia no momento." if st.session_state.language == 'pt-br' else "No hay otras noticias en este momento."
                st.info(no_news_other)
    else:
        with tab1:
            st.info(t['no_news'])
        with tab2:
            st.info(t['no_news'])

# ============================================
# FOOTER COM INFORMAÇÕES PROFISSIONAIS
# ============================================
footer_bio_pt = "Especialista em Ciência de Dados e IA | Jornalista | Desenvolvedor de Soluções Avançadas"
footer_bio_es = "Especialista en Ciencia de Datos e IA | Periodista | Desarrollador de Soluciones Avanzadas"
footer_bio = footer_bio_pt if st.session_state.language == 'pt-br' else footer_bio_es

st.markdown("---")
st.markdown(f"""
<div style="text-align: center; padding: 1.5rem 0; color: {theme['text_muted']};">
    <div style="font-size: 1.1rem; font-weight: 600; color: {theme['accent']}; margin-bottom: 0.25rem;">
        📡 {t['footer_title']}
    </div>
    <div style="font-size: 0.9rem; margin-bottom: 1rem; font-style: italic; color: {theme['text_secondary']};">
        {t['footer_subtitle']}
    </div>
    <div style="margin-bottom: 1rem; color: {theme['text_secondary']};">
        Streamlit + Python + GoogleNews + Altair
    </div>
    <div style="border-top: 1px solid {theme['border']}; padding-top: 1rem; margin-top: 1rem;">
        <div style="font-weight: 600; color: {theme['accent']}; margin-bottom: 0.5rem;">Lenon de Paula</div>
        <div style="font-size: 0.85rem; color: {theme['text_secondary']}; margin-bottom: 0.75rem;">
            {footer_bio}
        </div>
        <div style="margin-bottom: 0.75rem;">
            <a href="mailto:lenondpaula@gmail.com" style="color: {theme['accent']}; text-decoration: none; margin: 0 8px;">📧 lenondpaula@gmail.com</a>
            <a href="https://wa.me/5555981359099" style="color: {theme['accent']}; text-decoration: none; margin: 0 8px;">💬 +55 (55) 98135-9099</a>
        </div>
        <div style="margin-bottom: 0.75rem;">
            <a href="https://www.linkedin.com/in/lenonmpaula/" style="color: {theme['accent']}; text-decoration: none; margin: 0 8px;">🔗 LinkedIn</a>
            <a href="https://github.com/lenondpaula" style="color: {theme['accent']}; text-decoration: none; margin: 0 8px;">🐙 GitHub</a>
            <a href="https://t.me/+5555981359099" style="color: {theme['accent']}; text-decoration: none; margin: 0 8px;">📲 Telegram</a>
            <a href="https://goodluke.streamlit.app/" style="color: {theme['accent']}; text-decoration: none; margin: 0 8px;">🧪 GoodLuke AI Hub</a>
        </div>
        <div style="font-size: 0.85rem; color: {theme['text_muted']}; margin-top: 1rem;">
            © 2026 Lenon de Paula
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
