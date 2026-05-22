import streamlit as st
import os
import json
from utils import extract_text_from_pdf, generate_script, save_assets_dir, get_bgg_game_images, download_image, run_generate_audio, search_game_images_ddg, render_video

# Page configuration
st.set_page_config(
    page_title="Fábrica Autônoma de Vídeos",
    page_icon="🎬",
    layout="wide"
)

# Initialize session state for script and game data
if "script" not in st.session_state:
    st.session_state.script = None
if "game_path" not in st.session_state:
    st.session_state.game_path = None
if "bgg_images" not in st.session_state:
    st.session_state.bgg_images = None

# --- SIDEBAR (Configurações) ---
st.sidebar.title("⚙️ Configurações")
game_name = st.sidebar.text_input("Nome do Jogo", placeholder="Ex: Catan, Azul, Dixit...")
manual_file = st.sidebar.file_uploader("Upload do Manual (PDF)", type=["pdf"])
video_level = st.sidebar.selectbox(
    "Nível do Vídeo",
    ["Iniciante", "Avançado", "Estratégico"],
    help="Define o tom e a complexidade do roteiro gerado pela IA."
)

if st.sidebar.button("Salvar Configurações"):
    if game_name:
        st.session_state.game_path = save_assets_dir(game_name)
        st.sidebar.success(f"Configurações para '{game_name}' salvas!")
    else:
        st.sidebar.error("Por favor, insira o nome do jogo.")

# --- MAIN INTERFACE ---
st.title("🎬 Fábrica Autônoma de Vídeos Didáticos")
st.markdown("### Transforme manuais de jogos em vídeos verticais prontos para redes sociais.")

tab1, tab2, tab3 = st.tabs([
    "📝 Aba 1: Roteiro", 
    "🎙️ Aba 2: Narração & Imagens", 
    "✨ Aba 3: Animação & Vídeo Final"
])

# --- TAB 1: ROTEIRO ---
with tab1:
    st.header("1. Geração de Roteiro")
    if not game_name or not manual_file:
        st.warning("⚠️ Por favor, preencha o nome do jogo e faça o upload do manual na barra lateral.")
    else:
        st.info(f"Pronto para processar o jogo: **{game_name}**")
        
        if st.button("Gerar Roteiro com IA"):
            with st.spinner("Lendo manual e gerando roteiro..."):
                temp_pdf_path = f"temp_{manual_file.name}"
                with open(temp_pdf_path, "wb") as f:
                    f.write(manual_file.getbuffer())
                
                text = extract_text_from_pdf(temp_pdf_path)
                script = generate_script(game_name, text, video_level)
                os.remove(temp_pdf_path)
                
                if isinstance(script, (list, dict)):
                    if isinstance(script, dict) and "scenes" in script:
                        st.session_state.script = script["scenes"]
                    else:
                        st.session_state.script = script
                    st.success("Roteiro gerado com sucesso!")
                else:
                    st.error(f"Erro: {script}")

        if st.session_state.script:
            st.subheader("📝 Roteiro Editável")
            edited_script = []
            scenes_list = st.session_state.script
            if isinstance(scenes_list, dict):
                for key in ["scenes", "roteiro", "cenas", "items"]:
                    if key in scenes_list and isinstance(scenes_list[key], list):
                        scenes_list = scenes_list[key]
                        break
            
            if not isinstance(scenes_list, list):
                st.error("O formato do roteiro gerado não é uma lista válida.")
            else:
                for i, scene in enumerate(scenes_list):
                    s_num = scene.get("scene", scene.get("cena", i + 1))
                    s_visual = scene.get("visual", scene.get("imagem", "Descreva o visual aqui"))
                    s_narration = scene.get("narration", scene.get("texto", scene.get("narracao", "")))
                    
                    with st.expander(f"Cena {s_num}: {s_visual[:50]}...", expanded=True):
                        col_v, col_n = st.columns([1, 2])
                        new_visual = col_v.text_input(f"Visual {i}", value=s_visual, key=f"vis_{i}")
                        new_narration = col_n.text_area(f"Narração {i}", value=s_narration, key=f"nar_{i}")
                        edited_script.append({
                            "scene": s_num,
                            "visual": new_visual,
                            "narration": new_narration
                        })
                
                if st.button("Salvar Alterações no Roteiro"):
                    st.session_state.script = edited_script
                    st.success("Alterações salvas!")

# --- TAB 2: NARRAÇÃO & IMAGENS ---
with tab2:
    st.header("2. Ativos (Áudio e Imagens)")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🖼️ Imagens do Jogo")
        if not game_name:
            st.warning("⚠️ Insira o nome do jogo na barra lateral para liberar as ferramentas de imagem.")
        else:
            search_query = st.text_input("Termo de Busca de Imagem (ajuste se necessário)", value=f"{game_name} board game")
            
            if st.button("Buscar Imagens na Web"):
                with st.spinner("Buscando imagens reais na web..."):
                    results = search_game_images_ddg(search_query, max_results=5)
                    if results:
                        st.session_state.bgg_images = results
                        st.success(f"{len(results)} imagens encontradas!")
                    else:
                        st.error("Nenhuma imagem encontrada. Tente ajustar o termo de busca ou use a URL manual abaixo.")
            
            st.divider()
            manual_url = st.text_input("Ou cole a URL direta de uma imagem real (fallback):")
            if st.button("Usar URL Manual"):
                if manual_url:
                    st.session_state.bgg_images = {"main_image": manual_url}
                    st.success("URL manual configurada!")
            
            if st.session_state.bgg_images:
                st.divider()
                if isinstance(st.session_state.bgg_images, list):
                    st.write("🔍 **Resultados Encontrados:**")
                    cols = st.columns(len(st.session_state.bgg_images))
                    for idx, img_opt in enumerate(st.session_state.bgg_images):
                        with cols[idx]:
                            st.image(img_opt["thumbnail"], caption=f"Opção {idx + 1}", use_container_width=True)
                    
                    selected_idx = st.selectbox(
                        "Escolha a melhor imagem para o vídeo:",
                        range(len(st.session_state.bgg_images)),
                        format_func=lambda x: f"Opção {x + 1} - {st.session_state.bgg_images[x]['title'][:40]}..."
                    )
                    
                    selected_img = st.session_state.bgg_images[selected_idx]
                    st.image(selected_img["main_image"], caption="Visualização Completa", use_container_width=True)
                    
                    if st.button("Confirmar e Baixar para Assets"):
                        with st.spinner("Baixando imagem..."):
                            path = download_image(selected_img["main_image"], game_name, "main_game.jpg")
                            if path:
                                st.success(f"Imagem salva com sucesso em: {path}")
                            else:
                                st.error("Erro ao baixar a imagem. Tente outra opção da lista.")
                else:
                    imgs = st.session_state.bgg_images
                    st.image(imgs["main_image"], caption="Imagem Manual Selecionada", use_container_width=True)
                    if st.button("Baixar para Assets"):
                        with st.spinner("Baixando imagem..."):
                            path = download_image(imgs["main_image"], game_name, "main_game.jpg")
                            if path:
                                st.success(f"Imagem salva em: {path}")
                            else:
                                st.error("Erro ao baixar a imagem de URL manual.")
            
    with col2:
        st.subheader("🎙️ Narração (TTS)")
        if not st.session_state.script:
            st.warning("Gere o roteiro na Aba 1 primeiro.")
        else:
            if st.button("Gerar Áudios de Todas as Cenas"):
                with st.spinner("Gerando narrações..."):
                    game_assets = save_assets_dir(game_name)
                    for scene in st.session_state.script:
                        s_num = scene.get("scene", 0)
                        text = scene.get("narration", "")
                        audio_path = os.path.join(game_assets, f"scene_{s_num}.mp3")
                        run_generate_audio(text, audio_path)
                    st.success(f"Áudios gerados em: {game_assets}")
            st.info("Os áudios serão usados na renderização final.")

# --- TAB 3: ANIMAÇÃO & VÍDEO FINAL ---
with tab3:
    st.header("3. Renderização Final")
    
    if not game_name or not st.session_state.script:
        st.warning("⚠️ Por favor, certifique-se de configurar o nome do jogo na barra lateral e gerar o roteiro na Aba 1.")
    else:
        st.subheader("📊 Status dos Ativos do Jogo")
        
        game_assets = save_assets_dir(game_name)
        image_exists = os.path.exists(os.path.join(game_assets, "main_game.jpg"))
        
        missing_audios = []
        scenes_list = st.session_state.script
        for scene in scenes_list:
            s_num = scene.get("scene", 0)
            audio_path = os.path.join(game_assets, f"scene_{s_num}.mp3")
            if not os.path.exists(audio_path):
                missing_audios.append(s_num)
                
        col_img, col_aud = st.columns(2)
        
        with col_img:
            st.write("🖼️ **Imagem Principal (Jogo):**")
            if image_exists:
                st.success("✅ Pronta (`main_game.jpg` encontrada)")
                st.image(os.path.join(game_assets, "main_game.jpg"), width=250)
            else:
                st.error("❌ Ausente (`main_game.jpg` não encontrada na pasta de assets)")
                st.caption("Acesse a **Aba 2** para buscar ou colar a URL da imagem e baixá-la.")
                
        with col_aud:
            st.write("🎙️ **Narrações das Cenas (Áudio):**")
            if not missing_audios:
                st.success(f"✅ Todos os {len(scenes_list)} áudios foram gerados!")
            else:
                st.error(f"❌ Ausente ({len(missing_audios)} de {len(scenes_list)} áudios não encontrados)")
                st.write(f"Cenas com áudio em falta: {', '.join(map(str, missing_audios))}")
                st.caption("Acesse a **Aba 2** e clique em 'Gerar Áudios de Todas as Cenas' para gerá-los.")
        
        st.divider()
        st.subheader("📹 Efeitos de Vídeo (Image-to-Video)")
        if st.button("Gerar Animações de IA"):
            st.write("*(A integração Image-to-Video será implementada na Fase 5)*")
            
        st.divider()
        st.subheader("🎬 Exportar MP4")
        
        if not image_exists or missing_audios:
            st.error("⚠️ Para renderizar o vídeo final, certifique-se de baixar a imagem e gerar todos os áudios na Aba 2.")
            st.button("Renderizar Vídeo Final", disabled=True)
        else:
            st.success("🎉 Todos os ativos foram validados! Pronto para compilar o vídeo final.")
            
            video_output = os.path.join(game_assets, "video_final.mp4")
            
            if st.button("Renderizar Vídeo Vertical (9:16)"):
                with st.spinner("Renderizando vídeo vertical premium com MoviePy e Pillow... Isso pode levar de 15 a 30 segundos."):
                    video_path = render_video(game_name, st.session_state.script)
                    if video_path and os.path.exists(video_path):
                        st.success("✨ Vídeo renderizado com sucesso!")
                    else:
                        st.error("Ocorreu um erro durante a renderização do vídeo. Verifique os logs.")
            
            if os.path.exists(video_output):
                st.markdown("### 🍿 Assista ao Vídeo Final")
                st.video(video_output)
                
                with open(video_output, "rb") as f:
                    st.download_button(
                        label="⬇️ Baixar Vídeo Final (MP4)",
                        data=f,
                        file_name=f"{game_name.lower().replace(' ', '_')}_video_final.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("Desenvolvido por Gemini CLI 🤖")
