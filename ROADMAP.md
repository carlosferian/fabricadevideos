# 🗺️ Roadmap de Evolução - Fábrica Autônoma de Vídeos

Este documento serve como guia cronológico e lógico para a evolução contínua da **Fábrica Autônoma de Vídeos**. Ele detalha os próximos passos organizados por fases de desenvolvimento, priorizando valor visual imediato e estabilidade técnica antes de custos adicionais de APIs externas.

> Para o histórico detalhado de tudo o que já foi entregue, veja o [HANDOFF.md](HANDOFF.md).

---

## ✅ Fases Concluídas

### Fase 0: Sistema Agnóstico de Tema
* Presets de **Tipo de Conteúdo** (Jogos de Tabuleiro & Cartas, Educacional & Curiosidades, Tutorial & Passo a Passo, Resenha & Reviews, Histórias & Narrativas, Listas & Rankings, Customizado/Geral) e **Profundidade do Roteiro** (Resumido, Detalhado, Aprofundado).
* Upload de PDF e contexto em texto livre se tornaram opcionais — a IA pode gerar o roteiro apenas a partir do nome do projeto.
* Busca de imagens generalizada (`search_images_web`) com filtros opcionais de palavras-chave para priorizar/evitar, substituindo as heurísticas exclusivas de jogos de tabuleiro.
* Aba "Board Game Geek (BGG)" agora é condicional, exibida apenas para o tipo de conteúdo "Jogos de Tabuleiro & Cartas".
* Correção da fonte das legendas (download automático de `Poppins-Bold.ttf`) para garantir qualidade visual consistente em qualquer sistema operacional.
* Nomenclatura generalizada de `game`/`jogo` para `project`/`projeto` em toda a interface e no backend.

### Fase 1: Quick Wins Visuais & Sonoros (Custo: R$ 0)
* **1.1 Música de Fundo (BGM) Dinâmica:** Pasta `assets/bg_music/` com trilhas livres de direitos, controle de seleção/volume na Aba 3 e mixagem via `moviepy`.
* **1.2 Templates Visuais:** Três estilos de renderização disponíveis (Clássico, Gradiente Moderno e Neon Dark), com gradiente de fundo gerado a partir da paleta de cores da imagem principal.

### Fase 2: Performance & Experiência de Usuário (UX)
* **2.1 Paralelização de TTS:** Geração de todos os `scene_X.mp3` em paralelo via `ThreadPoolExecutor`/`asyncio.gather`.
* **2.2 Vozes Premium (ElevenLabs):** Integração opcional com vozes ultra-realistas, com seleção de voz e chave de API configurável.

### Fase 3: Metadados Automatizados para Redes Sociais
* O LLM gera automaticamente títulos, legendas (TikTok/Reels) e hashtags com base no roteiro e no Tipo de Conteúdo selecionado (Aba 4), persistidos em `metadata.json`/`metadata.txt`.

---

## 🚀 Próximas Fases

## 🤖 Fase 4: IA Avançada & Animações Premium
*Adoção de inteligência artificial generativa de ponta (introduz custos adicionais por chamada de API).*

### 4.1 🎬 Image-to-Video (Animação 3D de Cenas)
* **Objetivo:** Dar movimento tridimensional às imagens estáticas de qualquer cena do vídeo.
* **Componentes:**
  * Integração com APIs externas de geração de vídeo por IA (Runway Gen-2/Gen-3, Luma Dream Machine ou Kling).
  * O pipeline gerará um clipe de 3 a 5 segundos animando a imagem original da cena (mantendo a fidelidade) para ser usado como base, substituindo o frame estático.

---

## 📅 Fase 5: Automação e Distribuição (Escala Industrial)
*Transformar a aplicação em um publicador automático ponta a ponta, para vídeos de qualquer nicho.*

### 5.1 📅 Agendamento e Postagem Direta
* **Objetivo:** Publicar os vídeos direto nas redes sociais pelo Streamlit.
* **Componentes:**
  * Integração com as APIs oficiais do TikTok Business, Instagram Graph API e YouTube Data API para agendamento automático.

### 5.2 📸 Motor de Imagens Ampliado
* **Objetivo:** Melhorar a descoberta de imagens de alta definição sem sair do app, para qualquer tema.
* **Componentes:**
  * Adicionar provedores de busca de imagens adicionais (ex: bancos de imagens livres de direitos).
  * Melhorar o ranking heurístico de `search_images_web` com aprendizado a partir dos filtros usados pelo usuário.
