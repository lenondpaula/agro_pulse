# 📡 AgroPulse Media Watch

**Monitoramento de Mídia em Tempo Real** — Clipagem e Rádio Escuta para o Agronegócio

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://agropulse.streamlit.app)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 🎯 Sobre o Projeto

**AgroPulse Media Watch** é uma aplicação de monitoramento de mídia focada no evento **Agro en Punta 2026** (Uruguai & Brasil). O sistema oferece:

- 📻 **Rádio Escuta** — Feed ao vivo com transcrições de emissoras do Mercosul
- 🌐 **Web News** — Integração com Google News para notícias reais
- 📊 **Social Buzz** — Monitoramento de menções em X, Instagram, Facebook, Threads, LinkedIn e TikTok
- 📈 **Análise de Sentimento** — Classificação automática: Positivo, Neutro, Negativo

---

## ✨ Features

| Feature | Descrição |
|---------|-----------|
| 🎙️ **Rádio Escuta** | Feed de transcrições com análise de sentimento em tempo real |
| 📰 **Notícias em Abas** | Separação entre "Agro en Punta" e "Outras Notícias" |
| 📊 **Gráficos Interativos** | Volume de menções por hora em 6 redes sociais |
| 🌙 **Temas Visuais** | Dark Mode, Grey Mode e White Mode |
| 🌐 **Internacionalização** | Interface em Português (BR) e Español (UY) |
| 📡 **Ticker Dinâmico** | Última menção em rádio em rolagem contínua |

---

## 🚀 Quick Start

### Instalação Local

```bash
# Clone o repositório
git clone https://github.com/lenondpaula/agro_pulse.git
cd agro_pulse

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
streamlit run app/main.py
```

Acesse: **http://localhost:8501**

### Deploy no Streamlit Cloud

Acesse: **https://agropulse.streamlit.app**

---

## 🛠️ Stack Tecnológica

| Tecnologia | Uso |
|------------|-----|
| **Streamlit** | Framework Web interativo |
| **Pandas** | Manipulação de dados |
| **Altair** | Visualizações de gráficos |
| **GoogleNews** | Coleta de notícias em tempo real |
| **Faker** | Simulação de dados de rádio e social |
| **Python 3.10+** | Linguagem base |

---

## 📁 Estrutura do Projeto

```
agro_pulse/
├── app/
│   └── main.py              # 🎯 Aplicação principal Streamlit
├── src/
│   └── media_engine.py      # 🔧 Motor de coleta e simulação de dados
├── .streamlit/
│   └── config.toml          # ⚙️ Configuração do tema e servidor
├── .github/
│   ├── copilot-instructions.md  # 🤖 Instruções para agentes de IA
│   └── workflows/
│       └── keep-alive.yml   # 🟢 GitHub Action para manter app ativa
├── requirements.txt         # 📦 Dependências Python
├── app.py                   # (legacy) Redirecionamento
└── README.md                # 📖 Este arquivo
```

---

## 🎨 Temas Visuais

A aplicação suporta 3 temas, selecionáveis na sidebar:

| Tema | Fundo | Destaque |
|------|-------|----------|
| 🌙 **Dark** | #0E1117 | #00FF88 |
| 🌫️ **Grey** | #2D3748 | #48BB78 |
| ☀️ **White** | #FFFFFF | #38A169 |

---

## 📻 Emissoras Monitoradas

| País | Emissora |
|------|----------|
| 🇺🇾 Uruguai | Rádio Rural (UY), Carve 850 AM |
| 🇧🇷 Brasil | Rádio Gaúcha (BR), Jovem Pan Agro |

---

## 📰 Veículos de Imprensa

- **El País Uruguay** | **El Observador** | **La Nación Campo**
- **Canal Rural** | **Agrolink** | **Notícias Agrícolas**
- **Valor Econômico**

---

## 📊 Redes Sociais Monitoradas

- **X** (ex-Twitter) | **Instagram** | **Facebook**
- **Threads** | **LinkedIn** | **TikTok**

---

## 🔧 Configuração

### Variáveis de Ambiente (opcional)

```bash
# Para usar a API do GoogleNews
# Nenhuma chave é necessária - biblioteca usa scraping
```

### Configuração do Streamlit

O arquivo `.streamlit/config.toml` define:
- Tema visual padrão (Dark Mode)
- Configurações de servidor
- CORS e XSRF

---

## 👨‍💻 Autor

**Lenon de Paula**  
Especialista em Ciência de Dados e IA | Jornalista | Desenvolvedor de Soluções Avançadas

- 📧 [lenondpaula@gmail.com](mailto:lenondpaula@gmail.com)
- 💼 [LinkedIn](https://www.linkedin.com/in/lenonmpaula/)
- 🐙 [GitHub](https://github.com/lenondpaula)
- 💬 [WhatsApp](https://wa.me/5555981359099)
- 🧪 [GoodLuke AI Hub](https://goodluke.streamlit.app/)

---

## 📄 Licença

Este projeto faz parte do portfólio de demonstração. © 2026 Lenon de Paula.

---

## 🔗 Links Úteis

- 🌐 **Aplicação**: [agropulse.streamlit.app](https://agropulse.streamlit.app)
- 📂 **Repositório**: [github.com/lenondpaula/agro_pulse](https://github.com/lenondpaula/agro_pulse)
- 🧪 **Portfolio**: [goodluke.streamlit.app](https://goodluke.streamlit.app)

---

*Desenvolvido com ❤️ para o Agronegócio do Mercosul*
