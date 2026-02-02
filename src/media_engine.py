"""
AgroPulse Media Watch - Media Engine
Motor de coleta e simulação de dados de mídia para monitoramento.
"""

import pandas as pd
from datetime import datetime, timedelta
from faker import Faker
import random

# Inicializa Faker com locale português
fake = Faker('pt_BR')


def get_web_news():
    """
    Busca notícias reais usando GoogleNews para termos relacionados ao agronegócio.
    Retorna DataFrame com: Hora, Veículo, Título, Link
    """
    try:
        from GoogleNews import GoogleNews
        
        # Configura GoogleNews para português
        googlenews = GoogleNews(lang='pt', region='BR')
        googlenews.set_period('1d')  # Últimas 24 horas
        
        all_news = []
        search_terms = ['Agro en Punta', 'Agronegócio Uruguai', 'Expoagro', 'Agricultura Mercosul']
        
        for term in search_terms:
            googlenews.clear()
            googlenews.search(term)
            results = googlenews.results()
            
            for item in results[:5]:  # Limita a 5 por termo
                # Processa o tempo de publicação (corrige "á" para "Há")
                raw_date = item.get('date', '')
                formatted_date = _format_news_date(raw_date)
                
                # Processa o link - GoogleNews retorna links que precisam de tratamento
                raw_link = item.get('link', '')
                formatted_link = _format_news_link(raw_link)
                
                all_news.append({
                    'Hora': formatted_date,
                    'Veículo': item.get('media', 'Fonte desconhecida'),
                    'Título': item.get('title', 'Sem título'),
                    'Link': formatted_link
                })
        
        if not all_news:
            # Fallback com dados simulados se não houver resultados
            return _simulate_web_news()
            
        return pd.DataFrame(all_news)
    
    except Exception as e:
        print(f"Erro ao buscar notícias: {e}. Usando dados simulados.")
        return _simulate_web_news()


def _format_news_date(raw_date):
    """
    Formata a data/hora de publicação retornada pelo GoogleNews.
    Corrige problemas como 'á X minutos' para 'Há X minutos'.
    """
    if not raw_date:
        return datetime.now().strftime('%H:%M')
    
    # Corrige o problema comum do GoogleNews: "á" em vez de "Há"
    formatted = str(raw_date)
    
    # Substitui padrões incorretos
    if formatted.startswith('á '):
        formatted = 'Há ' + formatted[2:]
    elif formatted.startswith('a '):
        formatted = 'Há ' + formatted[2:]
    
    # Garante que "Há" está com acento correto
    formatted = formatted.replace('Ha ', 'Há ').replace('ha ', 'Há ')
    
    return formatted


def _format_news_link(raw_link):
    """
    Formata o link retornado pelo GoogleNews.
    O GoogleNews pode retornar links relativos ou com redirecionamento.
    """
    if not raw_link or raw_link == '#':
        return '#'
    
    # Se já é um link completo, retorna
    if raw_link.startswith('http://') or raw_link.startswith('https://'):
        return raw_link
    
    # Se é um link relativo do Google News, adiciona o prefixo
    if raw_link.startswith('./') or raw_link.startswith('/'):
        return f'https://news.google.com{raw_link.lstrip(".")}'
    
    # Tenta adicionar https:// se parecer ser um domínio
    if '.' in raw_link and ' ' not in raw_link:
        return f'https://{raw_link}'
    
    return '#'


def _simulate_web_news():
    """
    Fallback: gera notícias simuladas quando GoogleNews não está disponível.
    Divididas em: Agro en Punta (foco principal) e Outros Temas.
    """
    
    # === NOTÍCIAS SOBRE AGRO EN PUNTA (FOCO PRINCIPAL) ===
    agro_en_punta_news = [
        {
            'Título': 'Agro en Punta 2026 reúne 15 mil produtores em Punta del Este',
            'Veículo': 'El País Uruguay',
            'Link': 'https://www.elpais.com.uy/agro',
            'Categoria': 'Agro en Punta'
        },
        {
            'Título': 'Ministros do Mercosul assinam acordos históricos no Agro en Punta',
            'Veículo': 'El Observador',
            'Link': 'https://www.elobservador.com.uy/agro',
            'Categoria': 'Agro en Punta'
        },
        {
            'Título': 'Startups agtech apresentam inovações no Agro en Punta 2026',
            'Veículo': 'La Nación Campo',
            'Link': 'https://www.lanacion.com.ar/economia/campo',
            'Categoria': 'Agro en Punta'
        },
        {
            'Título': 'Brasil e Uruguai firmam parceria para rastreabilidade bovina no evento',
            'Veículo': 'Canal Rural',
            'Link': 'https://www.canalrural.com.br',
            'Categoria': 'Agro en Punta'
        },
        {
            'Título': 'Agro en Punta destaca sustentabilidade como futuro do agronegócio',
            'Veículo': 'Agrolink',
            'Link': 'https://www.agrolink.com.br',
            'Categoria': 'Agro en Punta'
        },
        {
            'Título': 'Delegação brasileira de 500 produtores participa do Agro en Punta',
            'Veículo': 'Notícias Agrícolas',
            'Link': 'https://www.noticiasagricolas.com.br',
            'Categoria': 'Agro en Punta'
        },
        {
            'Título': 'Evento em Punta del Este movimenta US$ 2 bilhões em negócios',
            'Veículo': 'Valor Econômico',
            'Link': 'https://valor.globo.com/agronegocios',
            'Categoria': 'Agro en Punta'
        },
        {
            'Título': 'Tecnologia de precisão é destaque no pavilhão do Agro en Punta',
            'Veículo': 'El País Uruguay',
            'Link': 'https://www.elpais.com.uy/agro',
            'Categoria': 'Agro en Punta'
        },
    ]
    
    # === OUTRAS NOTÍCIAS DO AGRONEGÓCIO ===
    outras_noticias = [
        {
            'Título': 'Exportações agrícolas do Uruguai batem recorde em janeiro',
            'Veículo': 'El Observador',
            'Link': 'https://www.elobservador.com.uy/economia',
            'Categoria': 'Mercado'
        },
        {
            'Título': 'Preço da soja atinge máxima histórica nas bolsas internacionais',
            'Veículo': 'Valor Econômico',
            'Link': 'https://valor.globo.com/agronegocios',
            'Categoria': 'Commodities'
        },
        {
            'Título': 'Investimentos em irrigação crescem 40% na região do Mercosul',
            'Veículo': 'Canal Rural',
            'Link': 'https://www.canalrural.com.br',
            'Categoria': 'Investimentos'
        },
        {
            'Título': 'Pecuária uruguaia conquista novos mercados na Ásia',
            'Veículo': 'La Nación Campo',
            'Link': 'https://www.lanacion.com.ar/economia/campo',
            'Categoria': 'Exportação'
        },
        {
            'Título': 'Safra de trigo 2026 tem previsão recorde para Argentina e Brasil',
            'Veículo': 'Agrolink',
            'Link': 'https://www.agrolink.com.br',
            'Categoria': 'Safra'
        },
        {
            'Título': 'Dólar agro impulsiona exportações do agronegócio brasileiro',
            'Veículo': 'Notícias Agrícolas',
            'Link': 'https://www.noticiasagricolas.com.br',
            'Categoria': 'Câmbio'
        },
        {
            'Título': 'China aumenta importação de carne bovina do Mercosul em 25%',
            'Veículo': 'Valor Econômico',
            'Link': 'https://valor.globo.com/agronegocios',
            'Categoria': 'Exportação'
        },
        {
            'Título': 'Produtores do RS investem em agricultura regenerativa',
            'Veículo': 'Canal Rural',
            'Link': 'https://www.canalrural.com.br',
            'Categoria': 'Sustentabilidade'
        },
    ]
    
    now = datetime.now()
    all_news = []
    
    # Adiciona notícias do Agro en Punta
    for i, news in enumerate(agro_en_punta_news):
        time_offset = timedelta(minutes=random.randint(10, 360))
        news_time = now - time_offset
        all_news.append({
            'Hora': f'Há {int(time_offset.total_seconds() // 60)} min',
            'Veículo': news['Veículo'],
            'Título': news['Título'],
            'Link': news['Link'],
            'Categoria': news['Categoria']
        })
    
    # Adiciona outras notícias
    for i, news in enumerate(outras_noticias):
        time_offset = timedelta(minutes=random.randint(60, 720))
        news_time = now - time_offset
        hours = int(time_offset.total_seconds() // 3600)
        mins = int((time_offset.total_seconds() % 3600) // 60)
        if hours > 0:
            time_str = f'Há {hours}h {mins}min'
        else:
            time_str = f'Há {mins} min'
        all_news.append({
            'Hora': time_str,
            'Veículo': news['Veículo'],
            'Título': news['Título'],
            'Link': news['Link'],
            'Categoria': news['Categoria']
        })
    
    return pd.DataFrame(all_news)


def simulate_radio_listening():
    """
    Simula monitoramento de rádio com transcrições de emissoras do target.
    Retorna DataFrame com: Timestamp, Emissora, Transcrição, Sentimento
    """
    emissoras = [
        'Rádio Rural (UY)',
        'Carve 850 AM',
        'Rádio Gaúcha (BR)',
        'Jovem Pan Agro'
    ]
    
    # Transcrições simuladas por categoria de sentimento
    transcricoes_positivas = [
        '...o evento em Punta está movimentando o PIB da região...',
        '...excelente participação de produtores nesta edição...',
        '...expectativa de recordes de exportação para este ano...',
        '...o Ministro da Agricultura acaba de chegar sob aplausos...',
        '...inovações tecnológicas impressionam visitantes...',
        '...acordo comercial pode beneficiar milhares de produtores...',
        '...safra recorde anima o setor agropecuário...',
    ]
    
    transcricoes_neutras = [
        '...atenção para o trânsito chegando no centro de convenções...',
        '...a programação de hoje inclui palestras sobre sustentabilidade...',
        '...previsão do tempo indica céu aberto para os próximos dias...',
        '...credenciamento segue até às dezoito horas...',
        '...próximo painel discutirá política agrícola regional...',
        '...representantes de doze países confirmaram presença...',
    ]
    
    transcricoes_negativas = [
        '...produtores reclamam da burocracia para exportação...',
        '...atraso na liberação de crédito preocupa agricultores...',
        '...preços dos insumos seguem pressionando margens...',
        '...seca em algumas regiões causa perdas significativas...',
        '...protestos de caminhoneiros afetam logística do evento...',
        '...tensão comercial pode impactar mercado de grãos...',
        '...críticas à infraestrutura do local marcam abertura...',
    ]
    
    registros = []
    now = datetime.now()
    
    for i in range(20):
        # Gera timestamp retroativo (últimas 4 horas)
        time_offset = timedelta(minutes=random.randint(5, 240))
        timestamp = now - time_offset
        
        # Seleciona sentimento com distribuição: 40% positivo, 35% neutro, 25% negativo
        sentimento_roll = random.random()
        if sentimento_roll < 0.40:
            sentimento = 'Positivo'
            transcricao = random.choice(transcricoes_positivas)
        elif sentimento_roll < 0.75:
            sentimento = 'Neutro'
            transcricao = random.choice(transcricoes_neutras)
        else:
            sentimento = 'Negativo'
            transcricao = random.choice(transcricoes_negativas)
        
        registros.append({
            'Timestamp': timestamp.strftime('%H:%M:%S'),
            'Emissora': random.choice(emissoras),
            'Transcrição': transcricao,
            'Sentimento': sentimento
        })
    
    # Ordena por timestamp (mais recente primeiro)
    df = pd.DataFrame(registros)
    df = df.sort_values('Timestamp', ascending=False).reset_index(drop=True)
    
    return df


def simulate_social_buzz():
    """
    Gera dados numéricos de menções em redes sociais para gráficos de volume.
    Simula: X (ex-Twitter), Instagram, Facebook, Threads, LinkedIn, TikTok
    Retorna DataFrame com dados por hora e por plataforma.
    """
    now = datetime.now()
    registros = []
    
    # Gera dados das últimas 24 horas (a cada hora)
    for i in range(24):
        hora = now - timedelta(hours=23-i)
        
        # Simula picos de atividade em horários específicos
        hora_do_dia = hora.hour
        
        # Fator de multiplicação baseado no horário
        if 8 <= hora_do_dia <= 12:  # Manhã: alta atividade
            fator = 1.5
        elif 14 <= hora_do_dia <= 18:  # Tarde: pico de atividade
            fator = 2.0
        elif 19 <= hora_do_dia <= 22:  # Noite: atividade moderada
            fator = 1.2
        else:  # Madrugada: baixa atividade
            fator = 0.4
        
        # Simula cada rede social com perfis diferentes
        base_x = random.randint(120, 280)  # X é muito usado para notícias
        base_instagram = random.randint(80, 180)  # Instagram visual
        base_facebook = random.randint(60, 150)  # Facebook público mais amplo
        base_threads = random.randint(30, 90)  # Threads ainda crescendo
        base_linkedin = random.randint(40, 100)  # LinkedIn profissional
        base_tiktok = random.randint(50, 130)  # TikTok vídeos curtos
        
        x = int(base_x * fator)
        instagram = int(base_instagram * fator)
        facebook = int(base_facebook * fator)
        threads = int(base_threads * fator)
        linkedin = int(base_linkedin * fator)
        tiktok = int(base_tiktok * fator)
        
        total = x + instagram + facebook + threads + linkedin + tiktok
        
        registros.append({
            'Hora': hora.strftime('%H:00'),
            'HoraCompleta': hora,
            'X': x,
            'Instagram': instagram,
            'Facebook': facebook,
            'Threads': threads,
            'LinkedIn': linkedin,
            'TikTok': tiktok,
            'Total': total
        })
    
    return pd.DataFrame(registros)


def get_sentiment_summary(radio_df):
    """
    Retorna resumo de sentimentos do monitoramento de rádio.
    """
    if radio_df.empty:
        return {'Positivo': 0, 'Neutro': 0, 'Negativo': 0}
    
    counts = radio_df['Sentimento'].value_counts().to_dict()
    return {
        'Positivo': counts.get('Positivo', 0),
        'Neutro': counts.get('Neutro', 0),
        'Negativo': counts.get('Negativo', 0)
    }


# Teste das funções
if __name__ == '__main__':
    print("=== Testando Media Engine ===\n")
    
    print("1. Web News:")
    news_df = get_web_news()
    print(news_df.head())
    print()
    
    print("2. Radio Listening:")
    radio_df = simulate_radio_listening()
    print(radio_df.head())
    print()
    
    print("3. Social Buzz:")
    social_df = simulate_social_buzz()
    print(social_df.head())
    print()
    
    print("4. Sentiment Summary:")
    print(get_sentiment_summary(radio_df))
