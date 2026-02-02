# AgroPulse Media Watch - Instruções para Agentes de IA

## Visão Geral do Projeto

**AgroPulse Media Watch** é uma aplicação de **Monitoramento de Mídia** (Clipagem e Rádio Escuta) focada no evento **Agro en Punta 2026** no Uruguai e Brasil. Desenvolvida com Streamlit, oferece tema **High Contrast Dark Mode** para leitura rápida.

## Stack Tecnológica

- **Framework**: Streamlit (Python 3.10+)
- **Dados**: Pandas, GoogleNews (notícias reais), Faker (simulação)
- **Visualização**: Altair (gráficos de barras empilhadas)
- **Temas**: Dark (#0E1117), Grey (#2D3748), White (#FFFFFF)
- **Internacionalização**: PT-BR e ES-UY

## Estrutura do Projeto

```
agro_pulse/
├── app/
│   └── main.py              # Dashboard principal Streamlit
├── src/
│   └── media_engine.py      # Motor de coleta e simulação de dados
├── .streamlit/
│   └── config.toml          # Configuração do tema e servidor
├── .github/
│   ├── copilot-instructions.md
│   └── workflows/
│       └── keep-alive.yml   # GitHub Action para evitar sleep mode
├── requirements.txt         # Dependências Python
└── README.md
```

## Comandos de Desenvolvimento

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar aplicação principal
streamlit run app/main.py

# Porta padrão: 8501
```

## Arquitetura da Aplicação

### Módulo `src/media_engine.py`

| Função | Descrição |
|--------|-----------|
| `get_web_news()` | Busca notícias via GoogleNews, com fallback para dados simulados |
| `_format_news_date()` | Corrige formatação de datas ("á" → "Há") |
| `_format_news_link()` | Processa links relativos do GoogleNews |
| `_simulate_web_news()` | Gera notícias simuladas divididas por categoria |
| `simulate_radio_listening()` | Gera 20 transcrições de rádio com sentimento |
| `simulate_social_buzz()` | Gera dados de 6 redes sociais por hora |
| `get_sentiment_summary()` | Retorna contagem de sentimentos |

### Módulo `app/main.py`

| Componente | Descrição |
|------------|-----------|
| **Ticker Superior** | Última menção em rádio com animação CSS |
| **KPIs** | Web News (24h), Citações em Rádio, Sentimento Global |
| **Feed de Rádio** | Timeline com cards coloridos por sentimento |
| **Gráfico Social** | Barras empilhadas por hora (6 redes) |
| **Tabela de Notícias** | 2 abas: "Agro en Punta" e "Outras Notícias" |
| **Footer** | Informações profissionais do autor |

## Convenções de Código

### Idioma
- **Código**: Nomes em inglês (variáveis, funções)
- **Strings de UI**: Português brasileiro ou Espanhol (via TRANSLATIONS)
- **Commits**: Português brasileiro, formato semântico

### Estilo Python
- Funções: `snake_case` (ex: `simulate_radio_listening`)
- Docstrings: Português brasileiro, formato simples
- Type hints quando útil para clareza

### Padrão de Cores (Tema Dark)
```python
COLORS = {
    'bg_primary': '#0E1117',
    'bg_secondary': '#1A1F2E',
    'accent': '#00FF88',
    'text_primary': '#FAFAFA',
    'text_secondary': '#A0AEC0',
    'negative': '#FF4444'
}
```

## Fontes de Dados

### Emissoras de Rádio Monitoradas
- 🇺🇾 Rádio Rural (UY), Carve 850 AM
- 🇧🇷 Rádio Gaúcha (BR), Jovem Pan Agro

### Veículos de Imprensa
- El País Uruguay, El Observador, La Nación Campo
- Canal Rural, Agrolink, Notícias Agrícolas, Valor Econômico

### Redes Sociais
- X (ex-Twitter), Instagram, Facebook, Threads, LinkedIn, TikTok

## Notas para Agentes de IA

### Ao adicionar features
1. Mantenha compatibilidade com os 3 temas (dark, grey, white)
2. Use Altair para gráficos (consistência visual)
3. Adicione traduções em `TRANSLATIONS` para PT-BR e ES-UY
4. Dados simulados via Faker, dados reais via GoogleNews
5. Priorize layout responsivo com `st.columns()`

### Padrões de UI
- Use `st.markdown()` com `unsafe_allow_html=True` para cards customizados
- Emojis para identificação rápida (🎙️ Rádio, 🌐 Web, 📊 Social)
- Sentimento: 🟢 Positivo, ⚪ Neutro, 🔴 Negativo
- Abas (`st.tabs()`) para organizar conteúdo

### Foco Principal
O tema central é o **Agro en Punta 2026** — evento agropecuário em Punta del Este reunindo Brasil e Uruguai. Notícias sobre este tema devem ser priorizadas.

---

**Última atualização**: 2026-02-02  
**Status**: MVP funcional  
**Deploy**: https://agropulse.streamlit.app
