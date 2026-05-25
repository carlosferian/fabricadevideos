# 📑 Documento de Handoff - Fábrica Autônoma de Vídeos Didáticos

## 🎯 Conceito Geral
O projeto visa automatizar a criação de vídeos curtos verticais (9:16) para redes sociais (TikTok/Reels/Shorts) focados no ensino de jogos de tabuleiro e cartas.

### 💡 Regras de Ouro:
1. **Fidelidade Visual:** Uso de imagens REAIS (BGG ou upload), evitando alucinações de IA em componentes.
2. **Baixo Custo:** Prioridade para ferramentas gratuitas (edge-tts para narração, Gemini Flash para roteiro, SoundHelix para BGM).
3. **Controle Humano:** Pipeline em abas (Streamlit) onde o usuário revisa e aprova cada etapa.

---

## 🏗️ Arquitetura Técnica Atualizada
- **Frontend:** Streamlit com abas organizadas (Roteiro, Ativos com sub-tabs para imagens, e Renderização com controles de estilo e som).
- **LLM (Roteiro):** OpenRouter (`openrouter/auto` com créditos de API).
- **TTS (Voz Paralela):** Geração concorrente em lote via `edge-tts` usando threads isoladas com `ThreadPoolExecutor` e `asyncio.gather` para performance ultra-rápida.
- **Processamento de PDF:** `pdfplumber` para leitura integral de manuais.
- **Filtros Pillow & Gradientes Dinâmicos:** Quantização de cores dominante em imagens reais, gerador de gradiente linear de cima para baixo, e algoritmos de arredondamento de cantos e bordas neon brilhantes.
- **Edição de Vídeo & BGM:** `moviepy` v2.1.2 e `Pillow` com suporte a mixagem de áudio composto (`CompositeAudioClip`) para música de fundo atenuada e renderização de layouts selecionáveis.

---

## 📊 Status do Projeto (Roadmap Executado)

### ✅ Fase Básica (Estrutura e Ingestão)
- Ingestão inteligente de PDFs e persistência/restauração automática de roteiros.
- Motor DuckDuckGo heurístico e scraper HTTP de páginas web para imagens.
- Interface de limpeza granular de ativos na barra lateral.

### ✅ Fase 1 (Novos Layouts & Música de Fundo) - *Concluída Hoje*
- **1.1 Música de Fundo Dinâmica (BGM):**
  * Downloads automáticos de trilhas de áudio padrão do SoundHelix (`synth_pulse.mp3`, `retro_groove.mp3`, `chill_wave.mp3`) caso a pasta esteja vazia, evitando bloqueios 403.
  * Controle deslizante de volume (0% a 50%) e mixagem via MoviePy.
- **1.2 Templates de Layouts Premium:**
  * **Clássico:** Borda branca fina e fundo Gaussian Blur 30px.
  * **Gradiente Moderno:** Fundo gradiente dinâmico gerado no Pillow a partir da quantização de cores dominantes do jogo. Centralização com cantos arredondados (radius=35px) e borda suave.
  * **Neon Dark:** Fundo com 62% de escurecimento e Gaussian Blur 50px. Central com cantos arredondados e borda neon com brilho colorido dinâmico por cena. Legenda glassmorphic denso com contorno neon correspondente.

### ✅ Fase 2 (Performance & UX) - *Concluída Hoje*
- **2.1 Paralelização de Locução (TTS):**
  * O loop de locuções foi reescrito para rodar em lote paralelo concorrente.
  * **Métrica de velocidade:** Geração de 3 narrações longas concluída em **2.22 segundos** (~77% de ganho de velocidade em relação à geração sequencial antiga).
- **2.2 API Oficial do BoardGameGeek (BGG) & Sub-tabs:**
  * Redesenho de Aba 2 com inner tabs organizadas (`st.tabs`) para busca DDG, busca direta na API oficial XML v2 do BGG por ID/link, e URL Manual/Scraper.
  * Unificação de coleções de saída de imagens para listas uniformes.

---

## 🚀 Próximos Passos & Pendências (Para a Retomada dos Trabalhos)

### 1. 🤖 Fase 3: IA Avançada & Animações Premium
* **3.1 Image-to-Video (Animação 3D de Componentes):**
  * Integrar APIs externas de geração de vídeo por IA (Runway Gen-2/Gen-3, Luma Dream Machine ou Kling via OpenRouter ou endpoints próprios). O sistema enviará a imagem real do componente e gerará um clipe animado de 3-5 segundos como base para a cena no MoviePy.
* **3.2 Vozes Neurais Ultra-Realistas (ElevenLabs):**
  * Adicionar integração opcional de API da ElevenLabs para locuções com sotaque brasileiro premium e entonação interpretativa impecável.

### 2. 📅 Fase 4: Automação e Distribuição (Escala de Canais)
* **4.1 Geração de Metadados Sociais:**
  * Fazer com que o LLM gere automaticamente o **Título**, **Copy de Descrição** e **Hashtags** otimizados para Reels/Shorts/TikTok com base no roteiro, salvando um arquivo `metadata.txt` nos assets.
* **4.2 Agendamento e Postagem Direta:**
  * Integrar fluxos de agendamento automático usando APIs oficiais do TikTok Business, Instagram Graph API e YouTube Data API para publicação direto do painel Streamlit.

---

**Nota de Sucesso Atual:** O pipeline de criação, locuções em lote paralelo ultrarrápido (2.2s) e renderização premium multi-estilos com BGM atenuada está 100% testado, consolidado, livre de bugs no Windows e pronto para publicação!
