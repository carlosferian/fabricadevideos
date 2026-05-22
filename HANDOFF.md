# 📑 Documento de Handoff - Fábrica Autônoma de Vídeos Didáticos

## 🎯 Conceito Geral
O projeto visa automatizar a criação de vídeos curtos verticais (9:16) para redes sociais (TikTok/Reels/Shorts) focados no ensino de jogos de tabuleiro e cartas.

### 💡 Regras de Ouro:
1. **Fidelidade Visual:** Uso de imagens REAIS (BGG ou upload), evitando alucinações de IA em componentes.
2. **Baixo Custo:** Prioridade para ferramentas gratuitas (edge-tts para narração, Gemini Flash para roteiro).
3. **Controle Humano:** Pipeline em abas (Streamlit) onde o usuário revisa e aprova cada etapa.

---

## 🏗️ Arquitetura Técnica
- **Frontend:** Streamlit (3 abas: Roteiro, Ativos, Renderização).
- **LLM (Roteiro):** OpenRouter (atualmente usando `openrouter/auto` com créditos para máxima estabilidade).
- **TTS (Voz):** `edge-tts` (Vozes brasileiras neurais gratuitas).
- **Processamento de PDF:** `pdfplumber` para leitura integral do manual.
- **Edição de Vídeo:** `moviepy` (preparado para montagem).

---

## 📊 Status do Projeto (Roadmap)

### ✅ Fase 1: Estrutura Básica
- Repositório, `.gitignore`, `requirements.txt` e UI Shell no `app.py` concluídos.

### ✅ Fase 2: Ingestão e Roteiro
- Leitura de PDF e geração de roteiro JSON via OpenRouter funcionando.
- Sistema robusto para lidar com diferentes formatos de resposta do LLM.
- **Pasta de Assets:** Estrutura `assets/{nome_do_jogo}/` criada automaticamente.

### ⚠️ Fase 3: Imagens (BGG) - **BLOQUEADO/FALLBACK**
- **O Problema:** A API XML2 do BoardGameGeek passou a exigir `Bearer Token` (aprovação manual demora semanas) e o scraping direto via Python está sofrendo bloqueios de **Status 403**.
- **A Solução Implementada:** Fallback para **Entrada Manual**. O usuário pode inserir o ID do jogo ou, preferencialmente, colar a **URL direta de uma imagem** real encontrada na web.

### 🛠️ Fase 4: Narração (TTS)
- Integração com `edge-tts` concluída no `utils.py`.
- Lógica de geração de áudios individuais por cena implementada no `app.py`.

---

## 🚀 Próximos Passos (Para a Próxima IA)

1. **Validação de Ativos:** Garantir que o usuário tenha baixado a imagem (`main_game.jpg`) e gerado os áudios (`scene_X.mp3`) na Aba 2.
2. **Implementação da Fase 4.1 (Renderização Estática):**
   - Criar em `utils.py` uma função usando `moviepy` para:
     - Criar clips de imagem (9:16) para cada cena.
     - Sincronizar com a duração do áudio da respectiva cena.
     - Concatenar as cenas em um vídeo final.
3. **Fase 5: Image-to-Video:**
   - Integrar modelos de animação via OpenRouter (ex: Luma/Kling) para animar a imagem estática antes da montagem final.

---

**Nota para o Desenvolvedor:** Os arquivos `app.py` e `utils.py` estão sincronizados. A chave de API está no `.env`. O foco deve ser agora a Aba 3 (Renderização).
