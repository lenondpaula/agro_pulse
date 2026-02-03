# AgroPulse Media Watch - Instruções para Agentes de IA

## Visão Geral
Aplicação Streamlit para monitoramento de mídia focada no evento **Agro en Punta 2026** (Uruguai/Brasil). Usa GoogleNews para dados reais e Faker para simulação.

## Stack Tecnológica
- **Framework**: Streamlit (Python 3.10+)
- **Dados**: Pandas, GoogleNews, Faker
- **Visualização**: Altair (gráficos empilhados)
- **Temas**: Dark (#0E1117), Grey (#2D3748), White (#FFFFFF)

## Estrutura do Projeto
```
├── app/main.py          # Dashboard principal
├── src/media_engine.py  # Motor de dados (notícias, rádio, social)
├── .streamlit/config.toml # Tema e servidor
├── requirements.txt     # Dependências
```

## Comandos Essenciais
```bash
pip install -r requirements.txt
streamlit run app/main.py  # Porta 8501
```

## Arquitetura
- **main.py**: UI com KPIs, feed de rádio, gráfico social, tabela de notícias em abas
- **media_engine.py**: Funções `get_web_news()`, `simulate_radio_listening()`, `simulate_social_buzz()`, `get_sentiment_summary()`
- Dados simulados priorizam "Agro en Punta"; fallback para GoogleNews

## Convenções de Código
- **Nomes**: Inglês (snake_case para funções)
- **Docstrings**: Português simples
- **UI Strings**: Dict `TRANSLATIONS` (PT-BR/ES-UY)
- **Temas**: Dict `THEMES` com cores hex
- **Imports**: `sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))` para src/

## Padrões de UI
- `st.markdown(unsafe_allow_html=True)` para cards customizados
- Emojis: 🎙️ Rádio, 🌐 Web, 📊 Social
- Sentimento: 🟢 Positivo, ⚪ Neutro, 🔴 Negativo
- `st.tabs()` para organizar conteúdo; `st.columns()` para responsivo

## Fontes de Dados
- **Rádio**: Rádio Rural (UY), Rádio Gaúcha (BR)
- **Imprensa**: El País, Canal Rural, etc.
- **Social**: X, Instagram, Facebook, Threads, LinkedIn, TikTok

## Notas para Agentes de IA
- Mantenha compatibilidade com 3 temas
- Use Altair para gráficos consistentes
- Adicione traduções em `TRANSLATIONS`
- Priorize "Agro en Punta" em dados simulados
- Teste com `streamlit run` após mudanças

**Última atualização**: 2026-02-03  
**Deploy**: https://agropulse.streamlit.app
