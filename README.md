# 🎬 Fábrica Autônoma de Vídeos (Vertical Shorts/Reels/TikTok)

Uma plataforma inteligente e modular em Streamlit desenvolvida para transformar qualquer ideia, documento ou tópico em vídeos verticais (9:16) premium, prontos para publicação em redes sociais — **sem amarração a nenhum nicho específico**.

---

## 🎯 Visão Geral do Projeto
O objetivo primário desta ferramenta é facilitar a criação automatizada de conteúdos atraentes para o público mobile, sobre **qualquer assunto**: jogos de tabuleiro, receitas, curiosidades, tutoriais, resenhas, histórias, rankings e muito mais. O pipeline foi estruturado em quatro etapas interativas para garantir que o criador de conteúdo tenha controle e capacidade de edição em cada parte do processo, mantendo um custo de execução extremamente reduzido.

Na barra lateral, o usuário escolhe um **Tipo de Conteúdo** (preset de persona/tom) e uma **Profundidade do Roteiro**, que orientam a IA na geração do roteiro. Um manual em PDF ou um contexto em texto livre são **opcionais** — sem eles, a IA usa seu próprio conhecimento sobre o tema informado.

---

## ✨ Principais Funcionalidades

### 1. 📝 Aba 1: Geração e Edição de Roteiros
* **Tipo de Conteúdo & Profundidade:** Presets na barra lateral (Jogos de Tabuleiro & Cartas, Educacional & Curiosidades, Tutorial & Passo a Passo, Resenha & Reviews, Histórias & Narrativas, Listas & Rankings ou Customizado/Geral) definem a persona, o tom de voz e o tipo de imagem que a IA usa para escrever o roteiro, em três níveis de profundidade (Resumido, Detalhado, Aprofundado).
* **Ingestão Opcional:** Upload de PDF (manuais, artigos, materiais de referência) via `pdfplumber` **e/ou** um campo de texto livre para contexto/tópico. Se nenhum dos dois for informado, a IA gera o roteiro usando seu próprio conhecimento sobre o tema.
* **Geração por IA:** Criação de roteiros adaptados ao tipo de conteúdo e profundidade escolhidos, integrados com a API do OpenRouter.
* **Persistência e Histórico:** Gravação automática do roteiro gerado e de todas as alterações feitas manualmente em `assets/{nome_do_projeto}/script.json`.
* **Restauração Dinâmica:** Painel na barra lateral para recuperar de forma instantânea projetos criados anteriormente, carregando seus dados salvos sem exigir novos uploads.

### 2. 🎙️ Aba 2: Narração & Imagens do Projeto
* **Busca de Imagens na Web:** Motor de busca interativo com acentuação normalizada e filtros avançados opcionais (palavras-chave para priorizar/evitar), aplicável a qualquer tema — de produtos a paisagens.
* **HTTP Page Scraper:** Cole a URL de qualquer página da web (Wikipédia, blogs, lojas) ou link direto. O scraper inteligente inspeciona o `Content-Type` do link, extrai imagens válidas da estrutura HTML, e as renderiza em uma grade de visualização interativa de 5 colunas para download instantâneo.
* **Board Game Geek (BGG):** Quando o `Tipo de Conteúdo` é "Jogos de Tabuleiro & Cartas", uma aba extra permite buscar a imagem oficial direto da API XML v2 do BGG por ID ou link.
* **Leitura Automática de Disco:** Ao restaurar um projeto, a interface identifica se você já possui a imagem principal ou narrações e os exibe de forma automática na tela.
* **Narração Dinâmica (TTS):** Geração de faixas individuais de áudio de alta qualidade e vozes neurais brasileiras gratuitas integradas com o `edge-tts`, com opção premium via ElevenLabs.

### 3. 🎬 Aba 3: Renderização Final Premium
* **Validação Física de Ativos:** Verificação automática de todos os requisitos de vídeo (existência da imagem principal e áudios de cada cena) com checkmarks verdes interativos.
* **Motor Vertical 9:16 com 3 Estilos Visuais** (Clássico, Gradiente Moderno e Neon Dark):
  * Redimensiona e desfoca a imagem de fundo com desfoque gaussiano de alta qualidade para preencher o formato 1080x1920 sem distorções.
  * Centraliza a imagem do componente principal com borda, cantos arredondados ou brilho neon, dependendo do estilo.
  * Renderiza legendas dinâmicas em português usando fonte `Poppins-Bold` (com fallback automático), formatadas com quebras automáticas de linha sobre faixas semitransparentes.
  * Animações de câmera Ken Burns (Zoom In, Zoom Out, Pan ou Estática) por cena, definidas pela IA ou manualmente.
  * Música de fundo opcional com controle de volume e mixagem via MoviePy.
  * Compilação estável do arquivo `video_final.mp4` compatível com dispositivos mobile, player de vídeo do Streamlit e botão de download.

### 4. 🚀 Aba 4: Metadados Sociais (Copywriter IA)
* Gera automaticamente títulos, legendas (TikTok e Instagram/Reels) e hashtags otimizadas para o roteiro atual, adaptados ao `Tipo de Conteúdo` selecionado.
* Edição manual e persistência em `metadata.json`/`metadata.txt`, com botão de download.

### 🗑️ Painel de Limpeza de Ativos (Sidebar)
* Exclusão seletiva e granular de áudios, imagem principal, vídeo final, roteiro ou remoção completa física da pasta do projeto no disco com feedbacks claros e `st.rerun()` em tempo real.

### ♿ Acessibilidade Visual
* Folha de estilo CSS integrada globalmente no topo da aplicação que eleva a escala tipográfica de textos, caixas de diálogo, inputs de formulário e botões de **18px a 38px** para máxima legibilidade.

---

## 🛠️ Stack Tecnológico
* **Linguagem:** Python 3.10+
* **Frontend:** Streamlit
* **LLM (Roteiro & Metadados):** OpenRouter API (`openrouter/auto`)
* **Processamento de PDFs:** pdfplumber
* **Busca e Raspagem:** requests, re
* **Processamento de Áudio (TTS):** edge-tts, ElevenLabs (opcional), asyncio
* **Renderização e Vídeo:** moviepy, Pillow (PIL)

---

## 📦 Estrutura de Diretórios
```markdown
fabricadevideos/
├── assets/                  # Armazenamento de projetos e ativos
│   ├── fonts/               # Fonte Poppins-Bold baixada automaticamente
│   ├── bg_music/            # Trilhas de música de fundo
│   └── {nome_do_projeto}/   # Pasta individual do projeto
│       ├── main_image.jpg   # Imagem principal baixada
│       ├── script.json      # Roteiro persistido
│       ├── scene_X.mp3      # Narração em áudio da cena X
│       ├── scene_X.jpg      # Imagem específica da cena X (opcional)
│       ├── metadata.json    # Metadados sociais persistidos
│       └── video_final.mp4  # Vídeo compilado renderizado
├── app.py                   # Interface Streamlit e controle de estados
├── utils.py                 # Utilitários de backend (IA, TTS, Render, Busca de Imagens, Scraper)
├── requirements.txt         # Dependências do Python
├── .env                     # Variáveis de ambiente (Chaves de API)
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

### 3. Configurar as Chaves de API
Crie um arquivo chamado `.env` na raiz do projeto com a sua chave do OpenRouter (obrigatória) e, opcionalmente, a chave do ElevenLabs para narrações premium:
```env
OPENROUTER_API_KEY=sua_chave_api_aqui
ELEVENLABS_API_KEY=sua_chave_opcional_aqui
```

### 4. Executar a Aplicação Streamlit
```bash
streamlit run app.py
```

---

## 📝 Licença
Este projeto é de uso livre e acadêmico para fins de estudo e simplificação na fabricação de vídeos didáticos digitais de entretenimento.
