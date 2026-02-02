"""
AgroPulse Media Watch
Aplicação de Monitoramento de Mídia (Clipagem e Rádio Escuta)
Design: High Contrast Dark Mode
"""

import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
from faker import Faker
from GoogleNews import GoogleNews

# Configuração da página
st.set_page_config(
    page_title="AgroPulse Media Watch",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para High Contrast Dark Mode
st.markdown("""
<style>
    /* High Contrast Dark Mode */
    .stApp {
        background-color: #0E1117;
    }
    
    /* Cards com alto contraste */
    .metric-card {
        background: linear-gradient(135deg, #1A1F2E 0%, #0E1117 100%);
        border: 1px solid #00FF88;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    
    /* Títulos com destaque */
    .main-title {
        color: #00FF88;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0;
    }
    
    .subtitle {
        color: #FAFAFA;
        font-size: 1.1rem;
        text-align: center;
        opacity: 0.8;
        margin-top: 5px;
    }
    
    /* Alertas de mídia */
    .media-alert {
        background-color: #1A1F2E;
        border-left: 4px solid #00FF88;
        padding: 15px;
        margin: 10px 0;
        border-radius: 0 8px 8px 0;
    }
    
    .media-alert-urgent {
        border-left-color: #FF4444;
    }
    
    /* Tabelas com contraste */
    .dataframe {
        background-color: #1A1F2E !important;
    }
    
    /* Badges de fonte */
    .source-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 2px;
    }
    
    .source-tv { background-color: #FF6B6B; color: #0E1117; }
    .source-radio { background-color: #4ECDC4; color: #0E1117; }
    .source-web { background-color: #45B7D1; color: #0E1117; }
    .source-print { background-color: #96CEB4; color: #0E1117; }
</style>
""", unsafe_allow_html=True)


def init_faker():
    """Inicializa Faker com locale brasileiro"""
    return Faker('pt_BR')


def generate_mock_clips(fake: Faker, n: int = 50) -> pd.DataFrame:
    """Gera dados simulados de clipagem de mídia"""
    sources = ['TV', 'Rádio', 'Web', 'Impresso']
    sentiments = ['Positivo', 'Neutro', 'Negativo']
    channels = {
        'TV': ['Globo Rural', 'Canal Rural', 'Terraviva', 'Band News Agro'],
        'Rádio': ['CBN Agro', 'Jovem Pan Agro', 'Rádio Rural', 'Band FM Campo'],
        'Web': ['Agrolink', 'Canal Rural Web', 'Notícias Agrícolas', 'AgroPlus'],
        'Impresso': ['Globo Rural Revista', 'DBO', 'A Granja', 'Agrianual']
    }
    topics = [
        'Safra de Soja', 'Preço do Boi', 'Exportação de Grãos', 
        'Clima e Agricultura', 'Tecnologia no Campo', 'Sustentabilidade',
        'Crédito Rural', 'Mercado de Commodities', 'Pragas e Doenças',
        'Agricultura Familiar'
    ]
    
    data = []
    for _ in range(n):
        source = fake.random_element(sources)
        data.append({
            'data_hora': fake.date_time_between(start_date='-7d', end_date='now'),
            'fonte': source,
            'veiculo': fake.random_element(channels[source]),
            'titulo': fake.sentence(nb_words=8),
            'topico': fake.random_element(topics),
            'sentimento': fake.random_element(sentiments),
            'alcance': fake.random_int(min=1000, max=500000),
            'relevancia': fake.random_int(min=1, max=10)
        })
    
    return pd.DataFrame(data).sort_values('data_hora', ascending=False)


def fetch_real_news(query: str = "agronegócio brasil", lang: str = "pt") -> pd.DataFrame:
    """Busca notícias reais usando GoogleNews"""
    try:
        gn = GoogleNews(lang=lang, region='BR', period='7d')
        gn.search(query)
        results = gn.results()
        
        if results:
            df = pd.DataFrame(results)
            df = df.rename(columns={
                'title': 'titulo',
                'media': 'veiculo', 
                'date': 'data',
                'link': 'url'
            })
            return df[['titulo', 'veiculo', 'data', 'url']].head(20)
    except Exception as e:
        st.warning(f"Erro ao buscar notícias: {e}")
    
    return pd.DataFrame()


def create_sentiment_chart(df: pd.DataFrame) -> alt.Chart:
    """Cria gráfico de sentimento minimalista"""
    sentiment_counts = df['sentimento'].value_counts().reset_index()
    sentiment_counts.columns = ['sentimento', 'contagem']
    
    colors = {'Positivo': '#00FF88', 'Neutro': '#FAFAFA', 'Negativo': '#FF4444'}
    
    chart = alt.Chart(sentiment_counts).mark_arc(innerRadius=50).encode(
        theta=alt.Theta('contagem:Q'),
        color=alt.Color('sentimento:N', 
                       scale=alt.Scale(domain=list(colors.keys()), 
                                      range=list(colors.values()))),
        tooltip=['sentimento', 'contagem']
    ).properties(
        width=250,
        height=250,
        title='Sentimento da Mídia'
    ).configure_view(
        strokeWidth=0
    ).configure_title(
        color='#FAFAFA'
    ).configure_legend(
        labelColor='#FAFAFA',
        titleColor='#FAFAFA'
    )
    
    return chart


def create_timeline_chart(df: pd.DataFrame) -> alt.Chart:
    """Cria gráfico de timeline de menções"""
    df_timeline = df.copy()
    df_timeline['data'] = pd.to_datetime(df_timeline['data_hora']).dt.date
    timeline = df_timeline.groupby(['data', 'fonte']).size().reset_index(name='mencoes')
    
    chart = alt.Chart(timeline).mark_area(opacity=0.7).encode(
        x=alt.X('data:T', title='Data'),
        y=alt.Y('mencoes:Q', title='Menções', stack='zero'),
        color=alt.Color('fonte:N', 
                       scale=alt.Scale(scheme='set2')),
        tooltip=['data', 'fonte', 'mencoes']
    ).properties(
        width='container',
        height=300,
        title='Timeline de Menções por Fonte'
    ).configure_view(
        strokeWidth=0
    ).configure_axis(
        labelColor='#FAFAFA',
        titleColor='#FAFAFA',
        gridColor='#1A1F2E'
    ).configure_title(
        color='#FAFAFA'
    ).configure_legend(
        labelColor='#FAFAFA',
        titleColor='#FAFAFA'
    )
    
    return chart


def main():
    """Função principal da aplicação"""
    
    # Header
    st.markdown('<h1 class="main-title">📡 AgroPulse Media Watch</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Monitoramento de Mídia em Tempo Real | Clipagem & Rádio Escuta</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar - Filtros
    with st.sidebar:
        st.markdown("### 🎛️ Filtros")
        
        # Seleção de período
        periodo = st.selectbox(
            "Período",
            ["Últimas 24h", "Últimos 7 dias", "Últimos 30 dias"],
            index=1
        )
        
        # Seleção de fontes
        fontes = st.multiselect(
            "Fontes de Mídia",
            ["TV", "Rádio", "Web", "Impresso"],
            default=["TV", "Rádio", "Web", "Impresso"]
        )
        
        # Busca de tópicos
        topico_busca = st.text_input("🔍 Buscar tópico", placeholder="Ex: soja, milho...")
        
        st.markdown("---")
        
        # Toggle para dados reais
        usar_dados_reais = st.toggle("📰 Buscar notícias reais", value=False)
        
        if usar_dados_reais:
            query_news = st.text_input("Termo de busca", value="agronegócio brasil")
    
    # Inicializa dados
    fake = init_faker()
    df_clips = generate_mock_clips(fake, n=100)
    
    # Aplica filtros
    if fontes:
        df_clips = df_clips[df_clips['fonte'].isin(fontes)]
    
    if topico_busca:
        df_clips = df_clips[df_clips['topico'].str.contains(topico_busca, case=False, na=False)]
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📊 Total de Clippings",
            value=len(df_clips),
            delta=f"+{fake.random_int(5, 20)} hoje"
        )
    
    with col2:
        alcance_total = df_clips['alcance'].sum()
        st.metric(
            label="👥 Alcance Total",
            value=f"{alcance_total:,.0f}",
            delta="+12.5%"
        )
    
    with col3:
        positivos = len(df_clips[df_clips['sentimento'] == 'Positivo'])
        st.metric(
            label="✅ Menções Positivas",
            value=positivos,
            delta=f"{(positivos/len(df_clips)*100):.1f}%"
        )
    
    with col4:
        st.metric(
            label="📡 Veículos Monitorados",
            value=df_clips['veiculo'].nunique(),
            delta=None
        )
    
    st.markdown("---")
    
    # Gráficos
    col_chart1, col_chart2 = st.columns([1, 2])
    
    with col_chart1:
        st.altair_chart(create_sentiment_chart(df_clips), use_container_width=True)
    
    with col_chart2:
        st.altair_chart(create_timeline_chart(df_clips), use_container_width=True)
    
    st.markdown("---")
    
    # Tabs para diferentes visualizações
    tab1, tab2, tab3 = st.tabs(["📋 Clipagem Recente", "📻 Rádio Escuta", "📰 Notícias Reais"])
    
    with tab1:
        st.markdown("### 📋 Últimos Clippings")
        
        # Exibe clippings como cards
        for _, row in df_clips.head(10).iterrows():
            sentiment_color = {
                'Positivo': '🟢',
                'Neutro': '⚪',
                'Negativo': '🔴'
            }.get(row['sentimento'], '⚪')
            
            source_emoji = {
                'TV': '📺',
                'Rádio': '📻',
                'Web': '🌐',
                'Impresso': '📰'
            }.get(row['fonte'], '📄')
            
            with st.container():
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    st.markdown(f"""
                    **{source_emoji} {row['veiculo']}** | {row['data_hora'].strftime('%d/%m %H:%M')}  
                    {row['titulo']}  
                    `{row['topico']}` {sentiment_color} {row['sentimento']}
                    """)
                with col_b:
                    st.markdown(f"**Alcance:** {row['alcance']:,}")
                st.divider()
    
    with tab2:
        st.markdown("### 📻 Monitoramento de Rádio")
        
        df_radio = df_clips[df_clips['fonte'] == 'Rádio']
        
        if len(df_radio) > 0:
            for _, row in df_radio.head(8).iterrows():
                st.markdown(f"""
                <div class="media-alert">
                    <strong>📻 {row['veiculo']}</strong> - {row['data_hora'].strftime('%d/%m %H:%M')}<br>
                    {row['titulo']}<br>
                    <small>Tópico: {row['topico']} | Relevância: {'⭐' * row['relevancia']}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Nenhuma menção em rádio encontrada com os filtros atuais.")
    
    with tab3:
        st.markdown("### 📰 Notícias em Tempo Real")
        
        if usar_dados_reais:
            with st.spinner("Buscando notícias..."):
                df_news = fetch_real_news(query_news)
                
                if not df_news.empty:
                    for _, row in df_news.iterrows():
                        st.markdown(f"""
                        **🔗 [{row['titulo']}]({row['url']})**  
                        *{row['veiculo']}* - {row['data']}
                        """)
                        st.divider()
                else:
                    st.warning("Nenhuma notícia encontrada. Tente outro termo de busca.")
        else:
            st.info("Ative 'Buscar notícias reais' na barra lateral para ver notícias em tempo real.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #666;'>AgroPulse Media Watch © 2026 | "
        "Monitoramento inteligente para o agronegócio</p>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
