# 🗺️ Roadmap de Evolução - Fábrica Autônoma de Vídeos

Este documento serve como guia cronológico e lógico para a evolução contínua da **Fábrica Autônoma de Vídeos**. Ele detalha os próximos passos organizados por fases de desenvolvimento, priorizando valor visual imediato e estabilidade técnica antes de custos adicionais de APIs externas.

---

## 🎨 Fase 1: Quick Wins Visuais & Sonoros (Custo: R$ 0)
*Melhorias de alta percepção de valor com baixo esforço usando a infraestrutura local atual.*

### 1.1 🎙️ Música de Fundo (BGM) Dinâmica
* **Objetivo:** Adicionar trilha sonora de fundo nos vídeos de forma automática.
* **Componentes:**
  * Criação da pasta `assets/bg_music/` contendo arquivos `.mp3` livres de direitos autorais.
  * Adicionar um controle no Streamlit (Sidebar ou Aba 3) para selecionar a trilha sonora ou modo "Aleatório".
  * Integração no backend (`utils.py`) com `moviepy` para mesclar o áudio da música de fundo com a narração das cenas.
  * Ajuste automático de volume: a música deve ser atenuada (ex: -18dB) para não abafar a narração.

### 1.2 🖼️ Templates Visuais e Estilos de Renderização
* **Objetivo:** Oferecer layouts alternativos de vídeo para diversificação de canais.
* **Componentes:**
  * **Estilo Clássico (Atual):** Imagem centralizada com borda branca fina de 4px e fundo desfocado (Gaussian Blur 30px).
  * **Estilo Moderno (Gradiente Dinâmico):** Imagem com cantos arredondados e sombra projetada suave (*drop shadow*), posicionada sobre um fundo de gradiente linear/radial vibrante gerado automaticamente a partir das cores predominantes da imagem original do jogo (usando análise de paleta do Pillow).
  * **Estilo Neon/Tech:** Borda neon colorida brilhante ao redor do componente, com legendas em caixas de texto com cantos arredondados translúcidos.

---

## ⚙️ Fase 2: Performance & Experiência de Usuário (UX)
*Melhoria no desempenho, velocidade de renderização e precisão técnica das ferramentas.*

### 2.1 ⚡ Paralelização do Processamento de TTS
* **Objetivo:** Tornar a geração das locuções instantânea.
* **Componentes:**
  * Substituir o loop sequencial na geração das cenas na Aba 2 por processamento assíncrono paralelo com `asyncio.gather`.
  * Geração paralela de todos os arquivos `scene_X.mp3` em segundos.

### 2.2 📸 Motor de Imagens Ampliado
* **Objetivo:** Melhorar a descoberta de componentes do jogo sem sair do app.
* **Componentes:**
  * Adicionar scraper para extrair fotos da galeria oficial do BoardGameGeek (BGG).
  * Melhorar o ranking heurístico do DuckDuckGo para encontrar imagens de alta definição.

---

## 🤖 Fase 3: IA Avançada & Animações Premium
*Adoção de inteligência artificial generativa de ponta (introduz custos adicionais por chamada de API).*

### 3.1 🎬 Image-to-Video (Animação 3D de Componentes)
* **Objetivo:** Dar movimento tridimensional aos componentes estáticos do jogo.
* **Componentes:**
  * Integração com APIs externas de geração de vídeo por IA (Runway Gen-2/Gen-3, Luma Dream Machine ou Kling via OpenRouter/APIs).
  * O pipeline gerará um clipe de 3 a 5 segundos animando a imagem do componente original (mantendo a fidelidade) para ser usado como base da cena de vídeo, substituindo o frame estático.

### 3.2 🎙️ Vozes Ultra-Realistas (ElevenLabs)
* **Objetivo:** Locuções premium com entonação e tom interpretativo impecável.
* **Componentes:**
  * Integração opcional com a API do ElevenLabs.
  * Suporte para escolha de vozes com sotaque brasileiro extremamente naturais.

---

## 🚀 Fase 4: Automação e Distribuição (Escala Industrial)
*Transformar a aplicação em um publicador automático ponta a ponta.*

### 4.1 📝 Metadados Automatizados para Redes Sociais
* **Objetivo:** Gerar copys de postagem otimizadas para SEO e engajamento.
* **Componentes:**
  * O LLM gerará automaticamente o Título, Legenda e hashtags (TikTok, Reels, Shorts) baseados no roteiro criado na Aba 1.
  * Geração do arquivo `metadata.txt` na pasta de assets do jogo.

### 4.2 📅 Agendamento e Postagem Direta
* **Objetivo:** Publicar os vídeos direto nas redes sociais pelo Streamlit.
* **Componentes:**
  * Integração com as APIs oficiais do TikTok Business, Instagram Graph API e YouTube Data API para agendamento automático.
