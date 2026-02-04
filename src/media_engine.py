"""
AgroPulse Media Watch - Media Engine
Motor de coleta e simulação de dados de mídia para monitoramento.
"""

import pandas as pd
from datetime import datetime, timedelta
from faker import Faker
import random
import json
import os
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

# Inicializa Faker com locale português
fake = Faker('pt_BR')

# Caminho para cache de notícias
NEWS_CACHE_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'news_cache.json')

def _ensure_cache_dir():
    """Garante que o diretório de cache existe."""
    cache_dir = os.path.dirname(NEWS_CACHE_FILE)
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir, exist_ok=True)


def save_news_to_cache(news_df):
    """
    Salva notícias em cache JSON para persistência.
    Mantém histórico de 3 meses para Agro en Punta e 1 mês para outros.
    """
    if news_df.empty:
        return
    
    _ensure_cache_dir()
    
    # Carrega cache existente
    existing_cache = {}
    if os.path.exists(NEWS_CACHE_FILE):
        try:
            with open(NEWS_CACHE_FILE, 'r', encoding='utf-8') as f:
                existing_cache = json.load(f)
        except Exception:
            existing_cache = {}
    
    # Converte DataFrame para dict
    news_dict = news_df.to_dict('records')
    
    # Adiciona timestamp de armazenamento se não tiver
    now = datetime.now().isoformat()
    for item in news_dict:
        if '_cached_at' not in item:
            item['_cached_at'] = now
        if 'Categoria' not in item:
            # Detecta categoria automaticamente
            titulo = str(item.get('Título', '')).lower()
            item['Categoria'] = 'Agro en Punta' if 'agro en punta' in titulo else 'Outros'
    
    # Mescla com cache existente (evitando duplicatas por link)
    cached_links = {item.get('Link', ''): item for item in existing_cache.get('news', [])}
    for item in news_dict:
        link = item.get('Link', '')
        if link and link != '#':
            cached_links[link] = item
    
    # Salva cache atualizado
    try:
        with open(NEWS_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump({'news': list(cached_links.values())}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Erro ao salvar cache: {e}")


def load_cached_news(include_all=False):
    """
    Carrega notícias do cache com filtros de período.
    
    Args:
        include_all: Se True, retorna todas as notícias. Se False, aplica filtros.
    
    Retorna:
        DataFrame com notícias do cache filtradas por período.
    """
    if not os.path.exists(NEWS_CACHE_FILE):
        return pd.DataFrame()
    
    try:
        with open(NEWS_CACHE_FILE, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        news_list = cache_data.get('news', [])
        if not news_list:
            return pd.DataFrame()
        
        df = pd.DataFrame(news_list)
        
        if include_all:
            return df
        
        # Filtra por período baseado na categoria
        now = datetime.now()
        filtered = []
        
        for _, row in df.iterrows():
            categoria = row.get('Categoria', 'Outros')
            cached_at = row.get('_cached_at')
            
            if cached_at:
                try:
                    cached_dt = datetime.fromisoformat(cached_at)
                except ValueError:
                    cached_dt = now
            else:
                cached_dt = now
            
            idade_dias = (now - cached_dt).days
            
            if categoria == 'Agro en Punta' and idade_dias <= 90:  # 3 meses
                filtered.append(row)
            elif categoria != 'Agro en Punta' and idade_dias <= 30:  # 1 mês
                filtered.append(row)
        
        return pd.DataFrame(filtered) if filtered else pd.DataFrame()
    
    except Exception as e:
        print(f"Erro ao carregar cache: {e}")
        return pd.DataFrame()


def get_web_news(lang='pt-br'):
    """
    Busca notícias reais usando GoogleNews para termos relacionados ao agronegócio.
    Retorna DataFrame com: Hora, Veículo, Título, Link
    
    Args:
        lang: Idioma para fallback simulado ('pt-br' ou 'es-uy')
    """
    try:
        from GoogleNews import GoogleNews
        
        # Configura GoogleNews baseado no idioma
        if lang == 'es-uy':
            googlenews = GoogleNews(lang='es', region='UY')
        else:
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
                formatted_date = _format_news_date(raw_date, lang)
                
                # Processa o link - GoogleNews retorna links que precisam de tratamento
                raw_link = item.get('link', '')
                formatted_link = _format_news_link(raw_link)
                
                all_news.append({
                    'Hora': formatted_date,
                    'Veículo': item.get('media', 'Fonte desconhecida'),
                    'Título': item.get('title', 'Sem título'),
                    'Link': formatted_link
                })
        
        gdelt_news = get_gdelt_news(lang)
        df_gn = pd.DataFrame(all_news)
        combined = pd.concat([df_gn, gdelt_news], ignore_index=True)
        if combined.empty:
            # Fallback com dados simulados se não houver resultados
            combined = _simulate_web_news(lang)
        
        # Salva notícias no cache
        save_news_to_cache(combined)
        
        # Carrega cache completo (com histórico)
        cached = load_cached_news(include_all=False)
        if not cached.empty:
            return cached
        return combined
    
    except Exception as e:
        print(f"Erro ao buscar notícias: {e}. Usando dados simulados.")
        result = _simulate_web_news(lang)
        save_news_to_cache(result)
        return result


def _format_gdelt_time(seendate_str, lang='pt-br'):
    """
    Converte data GDELT (YYYYMMDDHHmmss) para formato relativo (Há X dias).
    """
    if not seendate_str or len(seendate_str) < 12:
        return 'Agora'
    
    try:
        seen_dt = datetime.strptime(seendate_str, '%Y%m%d%H%M%S')
        now = datetime.now()
        delta = now - seen_dt
        
        if delta.days > 0:
            if lang == 'es-uy':
                return f"Hace {delta.days} {'día' if delta.days == 1 else 'días'}"
            else:
                return f"Há {delta.days} {'dia' if delta.days == 1 else 'dias'}"
        elif delta.seconds >= 3600:
            hours = delta.seconds // 3600
            if lang == 'es-uy':
                return f"Hace {hours} {'hora' if hours == 1 else 'horas'}"
            else:
                return f"Há {hours} {'hora' if hours == 1 else 'horas'}"
        elif delta.seconds >= 60:
            mins = delta.seconds // 60
            if lang == 'es-uy':
                return f"Hace {mins} min"
            else:
                return f"Há {mins} min"
        else:
            return 'Agora' if lang == 'pt-br' else 'Ahora'
    except ValueError:
        return 'Agora' if lang == 'pt-br' else 'Ahora'


def _extract_veicle_from_url(url_str):
    """
    Extrai o nome do veículo/domínio da URL.
    """
    if not url_str:
        return 'Fonte GDELT'
    
    # Remove https:// e http://
    url_str = url_str.replace('https://', '').replace('http://', '')
    
    # Pega o domínio principal
    domain = url_str.split('/')[0].replace('www.', '')
    
    # Tira a extensão (.com, .com.br, etc)
    domain_parts = domain.split('.')
    if len(domain_parts) > 1:
        # Mantém o nome principal (ex: 'agrolink' em 'agrolink.com.br')
        veicle_name = domain_parts[0].capitalize()
        return veicle_name
    
    return 'Fonte GDELT'


def get_gdelt_news(lang='pt-br'):
    """
    Busca notícias via GDELT 2.1 Document API.
    Retorna DataFrame com: Hora, Veículo, Título, Link
    """
    search_terms = ['Agro en Punta', 'Agronegócio Uruguai', 'Expoagro', 'Agricultura Mercosul']
    source_lang = 'sourcelang:spa' if lang == 'es-uy' else 'sourcelang:por'
    all_news = []

    for term in search_terms:
        query = f'"{term}" {source_lang}'
        url = (
            'https://api.gdeltproject.org/api/v2/doc/doc?'
            f'query={quote_plus(query)}&mode=ArtList&maxrecords=20&format=json'
        )

        try:
            request = Request(url, headers={'User-Agent': 'AgroPulse/1.0'})
            with urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))

            for item in data.get('articles', []):
                seendate = item.get('seendate', '')
                hora = _format_gdelt_time(seendate, lang)
                
                # Tenta usar sourceCommonName, se não existir extrai da URL
                article_url = item.get('url', '')
                veicle = item.get('sourceCommonName', None)
                if not veicle or veicle == 'Unknown':
                    veicle = _extract_veicle_from_url(article_url)

                all_news.append({
                    'Hora': hora,
                    'Veículo': veicle,
                    'Título': item.get('title', 'Sem título'),
                    'Link': article_url
                })
        except Exception:
            continue

    return pd.DataFrame(all_news)


def _format_news_date(raw_date, lang='pt-br'):
    """
    Formata a data/hora de publicação retornada pelo GoogleNews.
    Corrige problemas como 'á X minutos' para 'Há X minutos' ou 'Hace X minutos'.
    
    Args:
        raw_date: Data bruta do GoogleNews
        lang: Idioma ('pt-br' ou 'es-uy')
    """
    if not raw_date:
        return datetime.now().strftime('%H:%M')
    
    formatted = str(raw_date)
    
    if lang == 'es-uy':
        # Para espanhol: converter para "Hace X minutos/horas"
        formatted = formatted.replace('á ', 'Hace ').replace('a ', 'Hace ')
        formatted = formatted.replace('Há ', 'Hace ').replace('Ha ', 'Hace ')
        formatted = formatted.replace('minutos', 'min').replace('horas', 'h')
        formatted = formatted.replace('hora', 'h').replace('minuto', 'min')
    else:
        # Para português: Corrige o problema comum do GoogleNews: "á" em vez de "Há"
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
    Remove parâmetros de tracking do Google (&ved, &usg, etc.)
    """
    if not raw_link or raw_link == '#':
        return '#'
    
    # Remove parâmetros de tracking do Google
    # O GoogleNews adiciona &ved=... e &usg=... aos links
    if '&ved=' in raw_link:
        raw_link = raw_link.split('&ved=')[0]
    if '&usg=' in raw_link:
        raw_link = raw_link.split('&usg=')[0]
    if '?ved=' in raw_link:
        raw_link = raw_link.split('?ved=')[0]
    
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




def _simulate_web_news(lang='pt-br'):
    """
    Fallback: gera notícias simuladas quando GoogleNews não está disponível.
    Divididas em: Agro en Punta (foco principal) e Outros Temas.
    Suporta internacionalização PT-BR e ES-UY.
    """
    
    # === NOTÍCIAS SOBRE AGRO EN PUNTA (FOCO PRINCIPAL) ===
    # Inclui links oficiais do evento, redes sociais e cobertura da imprensa
    agro_en_punta_news = {
        'pt-br': [
            # Links oficiais e redes sociais do evento
            {
                'Título': '🌐 Site Oficial: Agro en Punta 2026 - Programação Completa',
                'Veículo': 'Agro en Punta (Oficial)',
                'Link': 'https://www.agroenpunta.com',
                'Categoria': 'Agro en Punta'
            },
            {
                'Título': '📷 Instagram @agroenpunta - Cobertura ao vivo do evento',
                'Veículo': 'Instagram Oficial',
                'Link': 'https://www.instagram.com/agroenpunta',
                'Categoria': 'Agro en Punta'
            },
            {
                'Título': '🐦 X/Twitter @agroenpunta - Atualizações em tempo real',
                'Veículo': 'X (Twitter) Oficial',
                'Link': 'https://twitter.com/agroenpunta',
                'Categoria': 'Agro en Punta'
            },
            {
                'Título': '📘 Facebook Agro en Punta - Fotos e vídeos exclusivos',
                'Veículo': 'Facebook Oficial',
                'Link': 'https://www.facebook.com/agroenpunta',
                'Categoria': 'Agro en Punta'
            },
            {
                'Título': '🎬 YouTube Agro en Punta - Palestras e painéis ao vivo',
                'Veículo': 'YouTube Oficial',
                'Link': 'https://www.youtube.com/@agroenpunta',
                'Categoria': 'Agro en Punta'
            },
            # Cobertura da imprensa
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
                'Título': 'O boom de Punta del Este: evento agro transforma a região',
                'Veículo': 'Forbes Brasil',
                'Link': 'https://forbes.com.br/forbeslife/2025/11/o-boom-de-punta-del-este-descubra-a-cena-artistica-e-cultural-do-litoral-uruguaio/',
                'Categoria': 'Agro en Punta'
            },
            {
                'Título': 'Startups agtech apresentam inovações no Agro en Punta 2026',
                'Veículo': 'La Nación Campo',
                'Link': 'https://www.lanacion.com.ar/economia/campo',
                'Categoria': 'Agro en Punta'
            },
            {
                'Título': 'Brasil e Uruguai firmam parceria para rastreabilidade bovina',
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
            {
                'Título': 'Pecuária de elite: leilões batem recordes no Agro en Punta',
                'Veículo': 'Revista Globo Rural',
                'Link': 'https://globorural.globo.com',
                'Categoria': 'Agro en Punta'
            },
            {
                'Título': 'Uruguai se consolida como hub do agronegócio regional',
                'Veículo': 'Infobae',
                'Link': 'https://www.infobae.com/america/agro/',
                'Categoria': 'Agro en Punta'
            },
        ],
        'es-uy': [
            # Links oficiales y redes sociales del evento
            {
                'Título': '🌐 Sitio Oficial: Agro en Punta 2026 - Programación Completa',
                'Veículo': 'Agro en Punta (Oficial)',
                'Link': 'https://www.agroenpunta.com',
                'Categoria': 'Agro en Punta'
            },
            {
                'Título': '📷 Instagram @agroenpunta - Cobertura en vivo del evento',
                'Veículo': 'Instagram Oficial',
                'Link': 'https://www.instagram.com/agroenpunta',
                'Categoria': 'Agro en Punta'
            },
            {
                'Título': '🐦 X/Twitter @agroenpunta - Actualizaciones en tiempo real',
                'Veículo': 'X (Twitter) Oficial',
                'Link': 'https://twitter.com/agroenpunta',
                'Categoria': 'Agro en Punta'
            },
            {
                'Título': '📘 Facebook Agro en Punta - Fotos y videos exclusivos',
                'Veículo': 'Facebook Oficial',
                'Link': 'https://www.facebook.com/agroenpunta',
                'Categoria': 'Agro en Punta'
            },
            {
                'Título': '🎬 YouTube Agro en Punta - Conferencias y paneles en vivo',
                'Veículo': 'YouTube Oficial',
                'Link': 'https://www.youtube.com/@agroenpunta',
                'Categoria': 'Agro en Punta'
            },
            # Cobertura de prensa
            {
                'Título': 'Agro en Punta 2026 reúne 15 mil productores en Punta del Este',
                'Veículo': 'El País Uruguay',
                'Link': 'https://www.elpais.com.uy/agro',
                'Categoria': 'Agro en Punta'
            },
            {
                'Título': 'Ministros del Mercosur firman acuerdos históricos en Agro en Punta',
                'Veículo': 'El Observador',
                'Link': 'https://www.elobservador.com.uy/agro',
                'Categoria': 'Agro en Punta'
            },
            {
                'Título': 'El boom de Punta del Este: evento agro transforma la región',
                'Veículo': 'Forbes',
                'Link': 'https://forbes.com.br/forbeslife/2025/11/o-boom-de-punta-del-este-descubra-a-cena-artistica-e-cultural-do-litoral-uruguaio/',
                'Categoria': 'Agro en Punta'
            },
            {
                'Título': 'Startups agtech presentan innovaciones en Agro en Punta 2026',
                'Veículo': 'La Nación Campo',
                'Link': 'https://www.lanacion.com.ar/economia/campo',
                'Categoria': 'Agro en Punta'
            },
            {
                'Título': 'Brasil y Uruguay firman alianza para trazabilidad bovina',
                'Veículo': 'Canal Rural',
                'Link': 'https://www.canalrural.com.br',
                'Categoria': 'Agro en Punta'
            },
            {
                'Título': 'Agro en Punta destaca sostenibilidad como futuro del agronegocio',
                'Veículo': 'Agrolink',
                'Link': 'https://www.agrolink.com.br',
                'Categoria': 'Agro en Punta'
            },
            {
                'Título': 'Delegación brasileña de 500 productores participa en Agro en Punta',
                'Veículo': 'Noticias Agrícolas',
                'Link': 'https://www.noticiasagricolas.com.br',
                'Categoria': 'Agro en Punta'
            },
            {
                'Título': 'Evento en Punta del Este mueve US$ 2 mil millones en negocios',
                'Veículo': 'Valor Econômico',
                'Link': 'https://valor.globo.com/agronegocios',
                'Categoria': 'Agro en Punta'
            },
            {
                'Título': 'Tecnología de precisión es destaque en el pabellón del Agro en Punta',
                'Veículo': 'El País Uruguay',
                'Link': 'https://www.elpais.com.uy/agro',
                'Categoria': 'Agro en Punta'
            },
            {
                'Título': 'Ganadería de elite: remates baten récords en Agro en Punta',
                'Veículo': 'Revista Globo Rural',
                'Link': 'https://globorural.globo.com',
                'Categoria': 'Agro en Punta'
            },
            {
                'Título': 'Uruguay se consolida como hub del agronegocio regional',
                'Veículo': 'Infobae',
                'Link': 'https://www.infobae.com/america/agro/',
                'Categoria': 'Agro en Punta'
            },
        ]
    }
    
    # === OUTRAS NOTÍCIAS DO AGRONEGÓCIO ===
    outras_noticias = {
        'pt-br': [
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
                'Título': 'China aumenta importação de carne bovina do Mercosul em 25%',
                'Veículo': 'Valor Econômico',
                'Link': 'https://valor.globo.com/agronegocios',
                'Categoria': 'Exportação'
            },
        ],
        'es-uy': [
            {
                'Título': 'Exportaciones agrícolas de Uruguay baten récord en enero',
                'Veículo': 'El Observador',
                'Link': 'https://www.elobservador.com.uy/economia',
                'Categoria': 'Mercado'
            },
            {
                'Título': 'Precio de la soja alcanza máximo histórico en bolsas internacionales',
                'Veículo': 'Valor Econômico',
                'Link': 'https://valor.globo.com/agronegocios',
                'Categoria': 'Commodities'
            },
            {
                'Título': 'Inversiones en irrigación crecen 40% en la región del Mercosur',
                'Veículo': 'Canal Rural',
                'Link': 'https://www.canalrural.com.br',
                'Categoria': 'Inversiones'
            },
            {
                'Título': 'Ganadería uruguaya conquista nuevos mercados en Asia',
                'Veículo': 'La Nación Campo',
                'Link': 'https://www.lanacion.com.ar/economia/campo',
                'Categoria': 'Exportación'
            },
            {
                'Título': 'Cosecha de trigo 2026 tiene previsión récord para Argentina y Brasil',
                'Veículo': 'Agrolink',
                'Link': 'https://www.agrolink.com.br',
                'Categoria': 'Cosecha'
            },
            {
                'Título': 'China aumenta importación de carne bovina del Mercosur en 25%',
                'Veículo': 'Valor Econômico',
                'Link': 'https://valor.globo.com/agronegocios',
                'Categoria': 'Exportación'
            },
        ]
    }
    
    # Seleciona idioma
    agro_news = agro_en_punta_news.get(lang, agro_en_punta_news['pt-br'])
    other_news = outras_noticias.get(lang, outras_noticias['pt-br'])
    
    # Texto de tempo por idioma
    time_ago = 'Há' if lang == 'pt-br' else 'Hace'
    time_min = 'min' if lang == 'pt-br' else 'min'
    
    now = datetime.now()
    all_news = []
    
    # Adiciona notícias do Agro en Punta
    for i, news in enumerate(agro_news):
        time_offset = timedelta(minutes=random.randint(10, 360))
        all_news.append({
            'Hora': f'{time_ago} {int(time_offset.total_seconds() // 60)} {time_min}',
            'Veículo': news['Veículo'],
            'Título': news['Título'],
            'Link': news['Link'],
            'Categoria': news['Categoria']
        })
    
    # Adiciona outras notícias
    for i, news in enumerate(other_news):
        time_offset = timedelta(minutes=random.randint(60, 720))
        hours = int(time_offset.total_seconds() // 3600)
        mins = int((time_offset.total_seconds() % 3600) // 60)
        if hours > 0:
            time_str = f'{time_ago} {hours}h {mins}{time_min}'
        else:
            time_str = f'{time_ago} {mins} {time_min}'
        all_news.append({
            'Hora': time_str,
            'Veículo': news['Veículo'],
            'Título': news['Título'],
            'Link': news['Link'],
            'Categoria': news['Categoria']
        })
    
    return pd.DataFrame(all_news)


def simulate_radio_listening(lang='pt-br'):
    """
    Simula monitoramento de rádio com transcrições de emissoras do target.
    Retorna DataFrame com: Timestamp, Emissora, Transcrição, Sentimento
    
    Args:
        lang: Idioma das transcrições ('pt-br' ou 'es-uy')
    """
    emissoras = [
        'Rádio Rural (UY)',
        'Carve 850 AM',
        'Rádio Gaúcha (BR)',
        'Jovem Pan Agro'
    ]
    
    # Transcrições por idioma e sentimento
    transcricoes = {
        'pt-br': {
            'positivas': [
                '...o evento Agro en Punta está movimentando o PIB da região...',
                '...excelente participação de produtores nesta edição do Agro en Punta...',
                '...expectativa de recordes de exportação para este ano...',
                '...o Ministro da Agricultura acaba de chegar em Punta del Este sob aplausos...',
                '...inovações tecnológicas impressionam visitantes no pavilhão principal...',
                '...acordo comercial Brasil-Uruguai pode beneficiar milhares de produtores...',
                '...safra recorde anima o setor agropecuário no Mercosul...',
                '...organizadores comemoram recorde de público no Agro en Punta 2026...',
                '...presidente da Expointer confirma parceria histórica com Agro en Punta...',
                '...tecnologia de pecuária de precisão ganha destaque no evento...',
            ],
            'neutras': [
                '...atenção para o trânsito chegando no centro de convenções em Punta...',
                '...a programação de hoje inclui palestras sobre sustentabilidade agropecuária...',
                '...previsão do tempo indica céu aberto para os próximos dias em Punta del Este...',
                '...credenciamento de imprensa segue até às dezoito horas...',
                '...próximo painel discutirá política agrícola regional entre Brasil e Uruguai...',
                '...representantes de doze países confirmaram presença no Agro en Punta...',
                '...stand do Brasil apresenta novidades em agricultura regenerativa...',
                '...cotação do boi gordo se mantém estável nesta semana...',
            ],
            'negativas': [
                '...produtores reclamam da burocracia para exportação no Mercosul...',
                '...atraso na liberação de crédito rural preocupa agricultores...',
                '...preços dos insumos seguem pressionando margens dos produtores...',
                '...seca em algumas regiões do Sul causa perdas significativas...',
                '...protestos de caminhoneiros afetam logística do evento...',
                '...tensão comercial pode impactar mercado de grãos na região...',
                '...críticas à infraestrutura viária marcam primeiro dia do evento...',
            ]
        },
        'es-uy': {
            'positivas': [
                '...el evento Agro en Punta está moviendo el PIB de la región...',
                '...excelente participación de productores en esta edición de Agro en Punta...',
                '...expectativa de récords de exportación para este año...',
                '...el Ministro de Agricultura acaba de llegar a Punta del Este bajo aplausos...',
                '...innovaciones tecnológicas impresionan a los visitantes en el pabellón principal...',
                '...acuerdo comercial Uruguay-Brasil puede beneficiar a miles de productores...',
                '...cosecha récord anima al sector agropecuario en el Mercosur...',
                '...organizadores celebran récord de público en Agro en Punta 2026...',
                '...presidente de la Expo Prado confirma alianza histórica con Agro en Punta...',
                '...tecnología de ganadería de precisión gana destaque en el evento...',
            ],
            'neutras': [
                '...atención al tránsito llegando al centro de convenciones en Punta...',
                '...la programación de hoy incluye charlas sobre sustentabilidad agropecuaria...',
                '...pronóstico del tiempo indica cielo despejado para los próximos días en Punta del Este...',
                '...acreditación de prensa continúa hasta las dieciocho horas...',
                '...próximo panel discutirá política agrícola regional entre Uruguay y Brasil...',
                '...representantes de doce países confirmaron presencia en Agro en Punta...',
                '...stand de Uruguay presenta novedades en agricultura regenerativa...',
                '...cotización del ganado se mantiene estable esta semana...',
            ],
            'negativas': [
                '...productores reclaman por la burocracia para exportación en el Mercosur...',
                '...atraso en la liberación de crédito rural preocupa a los agricultores...',
                '...precios de los insumos siguen presionando márgenes de los productores...',
                '...sequía en algunas regiones del sur causa pérdidas significativas...',
                '...protestas de camioneros afectan logística del evento...',
                '...tensión comercial puede impactar mercado de granos en la región...',
                '...críticas a la infraestructura vial marcan primer día del evento...',
            ]
        }
    }
    
    # Seleciona o conjunto de transcrições baseado no idioma
    trans = transcricoes.get(lang, transcricoes['pt-br'])
    
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
            transcricao = random.choice(trans['positivas'])
        elif sentimento_roll < 0.75:
            sentimento = 'Neutro'
            transcricao = random.choice(trans['neutras'])
        else:
            sentimento = 'Negativo'
            transcricao = random.choice(trans['negativas'])
        
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
