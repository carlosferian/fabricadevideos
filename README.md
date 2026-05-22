# 🎬 Fábrica Autônoma de Vídeos Didáticos (Vertical Shorts/Reels/TikTok)

Uma plataforma inteligente e modular em Streamlit desenvolvida para transformar manuais complexos de jogos de tabuleiro e cartas em vídeos verticais (9:16) premium, prontos para publicação em redes sociais.

---

## 🎯 Visão Geral do Projeto
O objetivo primário desta ferramenta é facilitar a criação automatizada de conteúdos didáticos atraentes para o público mobile. O pipeline foi estruturado em três etapas interativas para garantir que o criador de conteúdo tenha controle e capacidade de edição em cada parte do processo, mantendo um custo de execução extremamente reduzido.

---

## ✨ Principais Funcionalidades

### 1. 📝 Aba 1: Geração e Edição de Roteiros
* **Ingestão Inteligente:** Upload de manuais de regras em PDF. O sistema faz a leitura e extração do texto por meio do `pdfplumber`.
* **Geração por IA:** Criação de roteiros com tom empolgante adaptados a três níveis de complexidade (Iniciante, Avançado e Estratégico) integrados com a API do OpenRouter.
* **Persistência e Histórico:** Gravação automática do roteiro gerado e de todas as alterações feitas manualmente em `assets/{nome_do_jogo}/script.json`.
* **Restauração Dinâmica:** Painel na barra lateral para recuperar de forma instantânea jogos criados anteriormente, carregando seus dados salvos sem exigir novos uploads de manuais.

### 2. 🎙️ Aba 2: Narração & Imagens do Jogo
* **Busca Heurística de Imagens (Bypassing BGG API):** Motor de busca web interativo alimentado por DuckDuckGo, com acentuação normalizada, ranqueamento inteligente por palavras-chave de boardgame e sistema rígido de filtro e penalização para ignorar imagens de bancos comerciais de mesmo nome (ex: "Banco de Venezuela").
* **HTTP Page Scraper:** Cole a URL de qualquer página da web (BoardGameGeek, Wikipédia, blogs) ou link direto. O scraper inteligente inspeciona o `Content-Type` do link, extrai imagens válidas da estrutura HTML, e as renderiza em uma grade de visualização interativa de 5 colunas para download instantâneo.
* **Leitura Automática de Disco:** Ao restaurar um jogo, a interface identifica se você já possui a imagem principal ou narrações e os exibe de forma automática na tela.
* **Narração Dinâmica (TTS):** Geração de faixas individuais de áudio de alta qualidade e vozes neurais brasileiras gratuitas integradas com o `edge-tts`.

### 3. 🎬 Aba 3: Renderização Final Premium
* **Validação Física de Ativos:** Verificação automática de todos os requisitos de vídeo (existência da imagem principal e áudios de cada cena) com checkmarks verdes interativos.
* **Motor Estático Vertical 9:16:** 
  * Redimensiona e desfoca a imagem do jogo com desfoque gaussiano de alta qualidade (Gaussian Blur 30px) para preencher os fundos sem distorções no formato 1080x1920.
  * Centraliza a imagem do componente original com uma borda branca fina de 4px.
  * Renderiza legendas dinâmicas em português, formatadas com quebras automáticas de linha sobre faixas retangulares pretas semitransparentes (opacidade de 70%).
  * Compilação estável do arquivo `video_final.mp4` compatível com dispositivos mobile, player de vídeo do Streamlit e botão de download.

### 🗑️ Painel de Limpeza de Ativos (Sidebar)
* Exclusão seletiva e granular de áudios, imagem principal, arquivo de roteiro ou remoção completa física da pasta do jogo no disco com feedbacks claros e st.rerun() em tempo real.

### ♿ Acessibilidade Visual
* Folha de estilo CSS integrada globalmente no topo da aplicação que eleva a escala tipográfica de textos, caixas de diálogo, inputs de formulário e botões de **18px a 38px** para máxima legibilidade.

---

## 🛠️ Stack Tecnológico
* **Linguagem:** Python 3.10+
* **Frontend:** Streamlit
* **Processamento de PDFs:** pdfplumber
* **Busca e Raspagem:** requests, re, duckduckgo_search
* **Processamento de Áudio (TTS):** edge-tts, asyncio
* **Renderização e Vídeo:** moviepy, Pillow (PIL)

---

## 📦 Estrutura de Diretórios
```markdown
fabricadevideos/
├── assets/                  # Armazenamento de jogos e ativos
│   └── {nome_do_jogo}/      # Pasta individual do jogo
│       ├── main_game.jpg    # Imagem principal baixada
│       ├── script.json      # Roteiro persistido
│       ├── scene_X.mp3      # Narração em áudio da cena X
│       └── video_final.mp4  # Vídeo compilado renderizado
├── app.py                   # Interface Streamlit e controle de estados
├── utils.py                 # Utilitários de backend (TTS, Render, DDG, Scraper)
├── requirements.txt         # Dependências do Python
├── .env                     # Variáveis de ambiente (Chave de API)
├── HANDOFF.md               # Detalhamento de arquitetura de desenvolvimento
└── README.md                # Documento descritivo do projeto (este arquivo)
```

---

## 🚀 Instalação e Execução

### 1. Clonar o Repositório e Acessar o Diretório
```bash
git clone https://github.com/carlosferian/fabricadevideos.git
cd fabricadevideos
```

### 2. Configurar o Ambiente Virtual (venv) e Instalar Dependências
```bash
python -m venv venv
# No Windows PowerShell:
.\venv\Scripts\Activate.ps1
# No Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configurar a Chave API do OpenRouter
Crie um arquivo chamado `.env` na raiz do projeto e insira a sua chave API:
```env
OPENROUTER_API_KEY=sua_chave_api_aqui
```

### 4. Executar a Aplicação Streamlit
```bash
streamlit run app.py
```

---

## 🧪 Testes Automatizados
O projeto conta com um script de validação de funcionalidades localizado na pasta do brain. Para rodar e certificar o funcionamento da persistência de arquivos, do HTTP Page Scraper e das rotinas de exclusão de ativos, execute com a venv ativa:
```bash
python C:\Users\quase\.gemini\antigravity-cli\brain\e88f51e8-1f29-4447-8fc3-2fe6f65a7723\scratch\test_new_features.py
```

---

## 📝 Licença
Este projeto é de uso livre e acadêmico para fins de estudo e simplificação na fabricação de vídeos didáticos digitais de entretenimento.
