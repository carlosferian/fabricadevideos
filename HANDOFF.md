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

### ✅ Fase Básica (Estrutura, Ingestão & Estabilidade)
- Ingestão inteligente de PDFs e persistência/restauração automática de roteiros.
- Motor DuckDuckGo heurístico e scraper HTTP de páginas web para imagens.
- Interface de limpeza granular de ativos na barra lateral.
- **Resolução de Bugs de Estabilidade:** Corrigido bug de `IndexError` no extrator de cores dominantes do Pillow para imagens de tons simples ou sólidos.

### ✅ Fase 1 (Novos Layouts & Música de Fundo)
- **1.1 Música de Fundo Dinâmica (BGM):**
  * Downloads automáticos de trilhas de áudio padrão do SoundHelix (`synth_pulse.mp3`, `retro_groove.mp3`, `chill_wave.mp3`) caso a pasta esteja vazia, evitando bloqueios 403.
  * Controle deslizante de volume (0% a 50%) e mixagem via MoviePy.
- **1.2 Templates de Layouts Premium:**
  * **Clássico:** Borda branca fina e fundo Gaussian Blur 30px.
  * **Gradiente Moderno:** Fundo gradiente dinâmico gerado no Pillow a partir da quantização de cores dominantes do jogo. Centralização com cantos arredondados (radius=35px) e borda suave.
  * **Neon Dark:** Fundo com 62% de escurecimento e Gaussian Blur 50px. Central com cantos arredondados e borda neon com brilho colorido dinâmico por cena. Legenda glassmorphic denso com contorno neon correspondente.

### ✅ Fase 2 (Performance & UX)
- **2.1 Paralelização de Locução (TTS):**
  * O loop de locuções foi reescrito para rodar em lote paralelo concorrente.
  * **Métrica de velocidade:** Geração de 3 narrações longas concluída em **2.22 segundos** (~77% de ganho de velocidade em relação à geração sequencial antiga).
- **2.2 API Oficial do BoardGameGeek (BGG) & Sub-tabs:**
  * Redesenho de Aba 2 com inner tabs organizadas (`st.tabs`) para busca DDG, busca direta na API oficial XML v2 do BGG por ID/link, e URL Manual/Scraper.
  * Unificação de coleções de saída de imagens para listas uniformes.

### ✅ Fase 3 (IA Avançada & Animações Premium - Concluída Hoje)
- **3.2 Vozes Neurais Ultra-Realistas (ElevenLabs):**
  * Integração opcional do ElevenLabs na Aba 2, com suporte a chaves no `.env` ou inserção direta e segura via interface.
  * Dropdown com vozes brasileiras de alto nível (Leticia, Gigi, Daniel e suporte a IDs customizados) processadas de forma concorrente em lote paralelo.
- **Animações de Câmera Ken Burns Locais:**
  * Efeitos elegantes de movimento de imagem (Zoom In, Zoom Out, Pan) processados localmente em memória combinando Pillow e MoviePy (custo zero de API e latência nula!).

### ✅ Fase 4 (Automação, Geração de Copies & Metadados Sociais - Concluída Hoje)
- **4.1 Geração de Metadados Sociais (Copywriter IA):**
  * Nova **Aba 4: Metadados Sociais** no Streamlit que analisa o roteiro via OpenRouter e gera automaticamente 3 títulos chamativos, 2 variações de legendas completas (uma para TikTok e outra para Instagram Reels com CTA) e hashtags estratégicas.
  * Suporte para edições manuais salvas no disco (`metadata.txt` e `metadata.json`) e botão para download direto.

### ✅ Fase 5 (Imagens e Animações Contextuais Semânticas por IA & Revitalização UX - Concluída Hoje)
- **5.1 Imagens Reais por Cena (Coerência Visual):**
  * O renderizador agora carrega imagens específicas por cena (`scene_1.jpg`, `scene_2.jpg`) correspondentes ao roteiro falado.
  * **Fallback Seguro:** Caso a cena não tenha imagem individual, o sistema usa a imagem principal `main_game.jpg` como fallback, mantendo 100% de estabilidade.
  * **Seletor de Download & Auto-Completar:** Adicionado dropdown de destino de download na Aba 2, atualizando automaticamente a pesquisa do DuckDuckGo com o visual exato da cena.
- **5.2 Animações Contextuais Semânticas:**
  * O prompt do OpenRouter exige o campo `'animation'` no JSON do roteiro.
  * A IA analisa a locução e seleciona o movimento de câmera perfeito (`Zoom In`, `Zoom Out`, `Pan` ou `Estática`).
  * Adicionado dropdown de edição manual da animação na Aba 1 e suporte ao novo modo global `"Contextual (Definido no Roteiro)"` na renderização Aba 3.
- **5.3 Interface Premium (SaaS Layout & Responsividade):**
  * Substituição de abas por **`streamlit-option-menu`** horizontal e régua de pipeline **`sac.steps`**.
  * Tema Dark Neon premium (fontes `Outfit`/`Inter` do Google Fonts, cartões glassmorphic, micro-animações de zoom nas imagens).
  * Correção de responsividade física contra corte de botões e inputs de texto (`white-space: normal`, ajuste de padding de containers).

---

## 🚀 Próximos Passos & Pendências (Para a Próxima Retomada dos Trabalhos)

### 1. 📅 Fase 4.2: Agendamento e Postagem Direta nas Redes Sociais
* **Objetivo:** Agendamento e publicação automatizada diretamente de dentro do painel do Streamlit.
* **Componentes:** Integrar com as APIs do TikTok Business, Instagram Graph API e YouTube Data API para Shorts/Reels.

### 2. 🎬 Fase 3.1: Image-to-Video (Animação 3D de Componentes por IA)
* **Objetivo:** Adicionar tridimensionalidade e movimentos realistas de vídeo aos componentes estáticos do jogo.
* **Componentes:** Conexão opcional com APIs externas de geração de vídeo (Kling, Luma Dream Machine ou Runway Gen-3) a partir do campo de chave de API inserido na Aba 3.

---

**Nota de Sucesso Atual:** O pipeline de criação de vídeos coerentes por cena com locuções inteligentes (ElevenLabs/Edge-TTS) e animações semânticas contextuais a custo zero de API está 100% consolidado, com layout SaaS responsivo reestruturado e pronto para os novos passos de postagem automatizada e IA 3D!
