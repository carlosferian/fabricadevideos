# 📑 Documento de Handoff - Fábrica Autônoma de Vídeos Didáticos

## 🎯 Conceito Geral
O projeto visa automatizar a criação de vídeos curtos verticais (9:16) para redes sociais (TikTok/Reels/Shorts) focados no ensino de jogos de tabuleiro e cartas.

### 💡 Regras de Ouro:
1. **Fidelidade Visual:** Uso de imagens REAIS (BGG ou upload), evitando alucinações de IA em componentes.
2. **Baixo Custo:** Prioridade para ferramentas gratuitas (edge-tts para narração, Gemini Flash para roteiro).
3. **Controle Humano:** Pipeline em abas (Streamlit) onde o usuário revisa e aprova cada etapa.

---

## 🏗️ Arquitetura Técnica
- **Frontend:** Streamlit (3 abas: Roteiro, Ativos, Renderização). Acessibilidade com CSS global para fontes ampliadas (18px a 38px).
- **LLM (Roteiro):** OpenRouter (`openrouter/auto` com créditos para máxima estabilidade).
- **TTS (Voz):** `edge-tts` (Vozes brasileiras neurais gratuitas) com gerador dinâmico de áudios.
- **Processamento de PDF:** `pdfplumber` para leitura integral do manual.
- **Edição de Vídeo & Imagens:** `moviepy` e `Pillow` (conversão 9:16 vertical, desfoque Gaussian Blur de fundo, centralização de fotos com borda premium, e legendas dinâmicas com quebra automática de linha sobre caixas semitransparentes).

---

## 📊 Status do Projeto (Roadmap)

### ✅ Fase 1: Estrutura Básica
- Repositório, `.gitignore`, `requirements.txt` e UI Shell no `app.py` concluídos.
- Folha de estilo de alta acessibilidade com fontes maiores.

### ✅ Fase 2: Ingestão e Roteiro
- Leitura de PDF e geração de roteiro JSON via OpenRouter.
- **Histórico e Persistência:** Roteiro salvo automaticamente em `assets/{game_name}/script.json`.
- **Restauração Dinâmica:** Seletor de histórico na barra lateral que preenche o jogo selecionado, sincroniza estados e carrega o roteiro salvo sem obrigar novo upload de manual em PDF.

### ✅ Fase 3: Imagens da Web (Bypassing BGG API)
- **Motor Bing Heurístico:** Motor de busca inteligente via DuckDuckGo com normalização de acentos, ranqueamento por relevância (focado em board games) e filtro de exclusão absoluta contra fotos de bancos comerciais (ex: "Banco de Venezuela" ao buscar "Banco Imobiliário").
- **Raspador Inteligente de Páginas Web (HTTP Scraper):** O usuário pode colar uma URL de página web (BoardGameGeek, Wikipédia, blogs) ou link direto. O scraper valida o `Content-Type` do link e extrai imagens úteis da página, exibindo-as em uma grade visual interativa de 5 colunas para seleção e download de caixa do jogo direto nos assets.

### ✅ Fase 4: Narração & Geração Física de Ativos (TTS)
- Integração com `edge-tts` e geração de áudios de cenas individuais.
- **Detecção Física em Tempo Real:** A Aba 2 e Aba 3 buscam fisicamente no disco e mostram o status dos ativos (ex: se `main_game.jpg` e os áudios individuais existem), atualizando o status dinamicamente.

### ✅ Fase 4.1: Renderização de Vídeo Vertical Premium
- Motor de renderização estática 9:16 concluído usando Pillow + MoviePy.
- Imagem estática centralizada com borda branca elegante sobre um fundo animado desfocado (Gaussian Blur 30px) do próprio jogo.
- Legendas dinâmicas em português, desenhadas com quebra de linha inteligente sobre fundo retangular preto semitransparentes (opacidade 70%).
- Compilação estável do arquivo `video_final.mp4` com codecs `libx264`/`aac` para compatibilidade nativa, player de vídeo do Streamlit e botão de download.

### ✅ Fase 4.2: Painel de Limpeza de Ativos (Gerenciamento)
- Painel `Limpeza de Ativos` em expander na barra lateral com botões de exclusão granular: remover apenas áudios, imagem principal, roteiro JSON ou limpar o jogo inteiro excluindo o diretório de assets físico e atualizando instantaneamente os status da UI via `st.rerun()`.

---

## 🚀 Próximos Passos (Para a Próxima IA)

1. **Fase 5: Image-to-Video (Animação):**
   - Integrar modelos de inteligência artificial de animação de imagem (como Luma, Kling ou Runway) via OpenRouter/APIs externas para dar movimento tridimensional aos componentes centrais do jogo antes de compilar com as legendas e áudio.
2. **Integração de Música de Fundo:**
   - Adicionar uma trilha sonora opcional com controle de volume em segundo plano para deixar os vídeos ainda mais dinâmicos e envolventes.

---

**Nota de Sucesso:** O pipeline de criação e compilação de vídeos verticais estáticos de alta qualidade está 100% testado, consolidado e integrado sem bugs de concorrência ou cache no Streamlit!
