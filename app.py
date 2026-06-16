import streamlit as st
import os
import json
from utils import extract_text_from_pdf, generate_script, save_assets_dir, get_bgg_game_images, download_image, run_generate_audio, search_images_web, render_video, save_script_to_file, load_script_from_file, extract_images_from_url, delete_project_assets, generate_social_metadata, create_scene_frame, CONTENT_TYPES, DEPTH_LEVELS, get_clips_dir, save_video_clip, get_clip_info, list_project_clips, delete_video_clip, assemble_clips
from streamlit_option_menu import option_menu
import streamlit_antd_components as sac

# Page configuration
st.set_page_config(
    page_title="Fábrica Autônoma de Vídeos",
    page_icon="🎬",
    layout="wide"
)

# Custom CSS to inject premium Dark Neon SaaS styling and custom fonts
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap');
    
    /* App-wide fonts & styling */
    html, body, p, span, li, label {
        font-family: 'Inter', sans-serif !important;
        font-size: 15px !important;
        color: #E2E8F0 !important;
    }
    
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
    }

    /* Headings styling */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        color: #F8FAFC !important;
        letter-spacing: -0.02em !important;
    }
    
    h1 {
        font-size: 38px !important;
        background: linear-gradient(135deg, #818CF8 0%, #EC4899 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Elegant Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0B0F19 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    section[data-testid="stSidebar"] hr {
        border-top-color: rgba(255, 255, 255, 0.08) !important;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
        padding-top: 2rem !important;
    }
    
    /* Universal Button Responsiveness & Wrapping (Crucial to prevent cut-offs) */
    button, .stButton > button {
        white-space: normal !important;
        word-wrap: break-word !important;
        word-break: break-word !important;
        height: auto !important;
        min-height: 38px !important;
        padding: 6px 14px !important;
        line-height: 1.25 !important;
        font-size: 14px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
    }
    
    /* Primary buttons with indigo-pink gradient and glow */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366F1 0%, #EC4899 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 14px 0 rgba(99, 102, 241, 0.35) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        width: 100% !important;
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px 0 rgba(236, 72, 153, 0.45) !important;
        color: #FFFFFF !important;
    }
    div.stButton > button[kind="primary"]:active {
        transform: translateY(0px) !important;
    }
    
    /* Secondary/normal buttons */
    div.stButton > button[kind="secondary"], div.stButton > button:not([kind="primary"]) {
        background: rgba(30, 41, 59, 0.6) !important;
        color: #F1F5F9 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }
    div.stButton > button:not([kind="primary"]):hover {
        background: rgba(51, 65, 85, 0.8) !important;
        border-color: rgba(99, 102, 241, 0.4) !important;
        color: #FFFFFF !important;
        transform: translateY(-1px) !important;
    }
    
    /* Inputs, textareas, and selectboxes - dark glassmorphic styling */
    div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea, div[data-baseweb="select"] > div {
        background-color: rgba(15, 23, 42, 0.5) !important;
        color: #F1F5F9 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px !important;
        font-size: 14px !important;
    }
    div[data-baseweb="input"]:focus-within, div[data-baseweb="textarea"]:focus-within {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
    }
    
    /* Global Expanders as beautiful cards */
    div[data-testid="stExpander"] {
        background: rgba(30, 41, 59, 0.4) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 12px !important;
        margin-bottom: 18px !important;
        box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.15) !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stExpander"]:hover {
        border-color: rgba(99, 102, 241, 0.25) !important;
        box-shadow: 0 6px 24px 0 rgba(0, 0, 0, 0.2) !important;
    }
    div[data-testid="stExpander"] summary {
        font-family: 'Outfit', sans-serif !important;
        font-size: 17px !important;
        font-weight: 600 !important;
        color: #F1F5F9 !important;
        padding: 12px 18px !important;
    }
    div[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        padding: 20px !important;
        background: rgba(15, 23, 42, 0.15) !important;
        border-top: 1px solid rgba(255, 255, 255, 0.04) !important;
    }
    
    /* Sleek custom sub-tabs */
    div[data-baseweb="tab-list"] {
        background-color: rgba(15, 23, 42, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 30px !important;
        padding: 4px !important;
        gap: 8px !important;
        margin-bottom: 1.5rem !important;
    }
    button[data-baseweb="tab"] {
        background: transparent !important;
        border: none !important;
        border-radius: 20px !important;
        padding: 8px 18px !important;
        color: #94A3B8 !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        transition: all 0.3s ease !important;
    }
    button[data-baseweb="tab"]:hover {
        color: #F1F5F9 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #6366F1 0%, #EC4899 100%) !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3) !important;
    }
    div[data-baseweb="tab-border"] {
        display: none !important;
    }
    
    /* Alert notifications styling */
    div[data-testid="stNotification"] {
        background: rgba(30, 41, 59, 0.65) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-left: 4px solid #6366F1 !important;
        border-radius: 12px !important;
        backdrop-filter: blur(12px) !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15) !important;
    }
    
    /* Hover scale for grid images */
    div[data-testid="stImage"] img {
        border-radius: 10px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    div[data-testid="stImage"] img:hover {
        transform: scale(1.04) !important;
        border-color: #EC4899 !important;
        box-shadow: 0 6px 20px rgba(236, 72, 153, 0.45) !important;
        cursor: pointer !important;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state for script and project data
if "script" not in st.session_state:
    st.session_state.script = None
if "project_path" not in st.session_state:
    st.session_state.project_path = None
if "bgg_images" not in st.session_state:
    st.session_state.bgg_images = None
if "project_name_val" not in st.session_state:
    st.session_state.project_name_val = ""
if "loaded_project_name" not in st.session_state:
    st.session_state.loaded_project_name = None
if "last_history_select" not in st.session_state:
    st.session_state.last_history_select = ""
if "script_version" not in st.session_state:
    st.session_state.script_version = 0

# --- SIDEBAR (Configurações) ---
st.sidebar.title("⚙️ Configurações")

# Histórico de projetos salvos em assets/ (ignora pastas internas de sistema)
existing_projects = [""]
if os.path.exists("assets"):
    folders = sorted([
        f for f in os.listdir("assets")
        if os.path.isdir(os.path.join("assets", f)) and f not in ("bg_music", "fonts")
    ])
    existing_projects.extend(folders)

selected_history = st.sidebar.selectbox(
    "📂 Restaurar Projeto Existente",
    options=existing_projects,
    index=0,
    format_func=lambda x: "Selecione um projeto..." if x == "" else x.replace("_", " ").title(),
    key="history_select"
)

# Atualizar o valor de busca/nome do projeto a partir da escolha do histórico (apenas quando houver mudança real de seleção)
if st.session_state.history_select != st.session_state.last_history_select:
    st.session_state.last_history_select = st.session_state.history_select
    if st.session_state.history_select != "":
        project_name_from_history = st.session_state.history_select.replace("_", " ").title()
        st.session_state.project_name_val = project_name_from_history
        st.session_state.project_name_input = project_name_from_history

project_name = st.sidebar.text_input(
    "Nome do Projeto / Vídeo",
    value=st.session_state.project_name_val,
    placeholder="Ex: Catan, Receita de Bolo de Cenoura, Top 5 Curiosidades do Espaço...",
    key="project_name_input"
)
st.session_state.project_name_val = project_name

# Carregar o script.json automaticamente na troca de projeto
if project_name != st.session_state.loaded_project_name:
    st.session_state.loaded_project_name = project_name
    if project_name:
        st.session_state.project_path = save_assets_dir(project_name)
        loaded_script = load_script_from_file(project_name)
        if loaded_script:
            st.session_state.script = loaded_script
            st.session_state.script_version += 1
            st.sidebar.info(f"📂 Roteiro de '{project_name}' carregado do histórico!")
        else:
            st.session_state.script = None
            st.session_state.bgg_images = None
    else:
        st.session_state.script = None
        st.session_state.bgg_images = None

st.sidebar.markdown("---")
st.sidebar.markdown("##### 🎯 Estilo do Roteiro")

content_type_options = list(CONTENT_TYPES.keys())
content_type = st.sidebar.selectbox(
    "Tipo de Conteúdo",
    options=content_type_options,
    index=content_type_options.index("Customizado / Geral"),
    help="Define a persona, o tom de voz e o tipo de imagem que a IA vai descrever para cada cena do roteiro."
)

depth_options = list(DEPTH_LEVELS.keys())
depth_level = st.sidebar.selectbox(
    "Profundidade do Roteiro",
    options=depth_options,
    index=depth_options.index("Detalhado"),
    help="Define a quantidade de cenas e o nível de detalhe do roteiro gerado pela IA."
)

st.sidebar.markdown("---")
st.sidebar.markdown("##### 📚 Fonte de Conteúdo (Opcional)")
manual_file = st.sidebar.file_uploader("Documento de Referência (PDF)", type=["pdf"])
context_text = st.sidebar.text_area(
    "Tópico / Contexto adicional",
    placeholder="Descreva o tema, cole um resumo, roteiro-base ou qualquer informação que a IA deva usar como referência...",
    height=120,
    help="Opcional. Se nenhum PDF ou contexto for informado, a IA usará seu próprio conhecimento sobre o tema."
)

if st.sidebar.button("Salvar Configurações"):
    if project_name:
        st.session_state.project_path = save_assets_dir(project_name)
        st.sidebar.success(f"Configurações para '{project_name}' salvas!")
    else:
        st.sidebar.error("Por favor, insira o nome do projeto/vídeo.")

# --- MAIN INTERFACE ---
st.markdown("<div style='text-align: center; margin-top: 1.5rem;'>", unsafe_allow_html=True)
st.title("🎬 Fábrica Autônoma de Vídeos")
st.markdown("<p style='font-size: 19px; color: #94A3B8; margin-top: 0px;'>Transforme qualquer ideia, documento ou roteiro em vídeos verticais premium para redes sociais.</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# Elegant Horizontal Navigation Menu
selected = option_menu(
    menu_title=None,
    options=["Roteiro", "Narração & Imagens", "Animação & Vídeo", "Clipes", "Metadados Sociais"],
    icons=["pencil-square", "mic", "play-btn", "film", "rocket-takeoff"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {
            "padding": "0!important", 
            "background-color": "#1E293B", 
            "border": "1px solid rgba(255, 255, 255, 0.08)", 
            "border-radius": "12px",
            "margin-bottom": "1.5rem"
        },
        "icon": {"color": "#EC4899", "font-size": "19px"}, 
        "nav-link": {
            "font-size": "16px", 
            "text-align": "center", 
            "margin": "0px", 
            "font-weight": "500", 
            "font-family": "Outfit, sans-serif", 
            "color": "#F1F5F9", 
            "--hover-color": "rgba(255, 255, 255, 0.05)"
        },
        "nav-link-selected": {
            "background": "linear-gradient(90deg, #6366F1 0%, #EC4899 100%)", 
            "font-weight": "600", 
            "color": "#FFFFFF"
        },
    }
)

# Render steps under the navigation for context
step_idx = 0
if selected == "Roteiro":
    step_idx = 0
elif selected == "Narração & Imagens":
    step_idx = 1
elif selected == "Animação & Vídeo":
    step_idx = 2
elif selected == "Clipes":
    step_idx = 3
elif selected == "Metadados Sociais":
    step_idx = 4

sac.steps(
    items=[
        sac.StepsItem(title='Roteiro', subtitle='Upload & Edição'),
        sac.StepsItem(title='Ativos', subtitle='Locução & Imagem'),
        sac.StepsItem(title='Renderização', subtitle='Efeitos & Vídeo'),
        sac.StepsItem(title='Clipes', subtitle='Montagem Livre'),
        sac.StepsItem(title='Distribuição', subtitle='Copies Redes'),
    ],
    index=step_idx,
    color='indigo',
    variant='standard',
    size='md'
)

st.markdown("<br>", unsafe_allow_html=True)

# --- TAB 1: ROTEIRO ---
if selected == "Roteiro":
    st.header("1. Geração de Roteiro")
    if not project_name:
        st.warning("⚠️ Por favor, preencha o nome do projeto/vídeo na barra lateral para começar.")
    else:
        if st.session_state.script:
            st.info(f"Roteiro carregado para o projeto: **{project_name}**")
        else:
            st.info(f"Pronto para gerar o roteiro para: **{project_name}** _(Tipo: {content_type})_")
            if not manual_file and not context_text:
                st.caption("💡 Dica: você pode gerar o roteiro apenas com o nome do projeto, mas adicionar um PDF ou contexto na barra lateral melhora a precisão das informações.")

        if st.button("Gerar Roteiro com IA"):
            with st.spinner("Lendo material de referência e gerando roteiro..."):
                source_text = ""
                if manual_file:
                    temp_pdf_path = f"temp_{manual_file.name}"
                    with open(temp_pdf_path, "wb") as f:
                        f.write(manual_file.getbuffer())
                    source_text += extract_text_from_pdf(temp_pdf_path)
                    os.remove(temp_pdf_path)

                if context_text:
                    source_text += "\n\n" + context_text

                script = generate_script(project_name, source_text, content_type, depth_level)

                if isinstance(script, (list, dict)):
                    if isinstance(script, dict) and "scenes" in script:
                        st.session_state.script = script["scenes"]
                    else:
                        st.session_state.script = script
                    st.session_state.script_version += 1
                    if project_name:
                        save_script_to_file(project_name, st.session_state.script)
                    st.success("Roteiro gerado e persistido no histórico com sucesso!")
                else:
                    st.error(f"Erro: {script}")

        if st.session_state.script:
            st.subheader("📝 Roteiro Editável")
            scenes_list = st.session_state.script
            if isinstance(scenes_list, dict):
                for key in ["scenes", "roteiro", "cenas", "items"]:
                    if key in scenes_list and isinstance(scenes_list[key], list):
                        scenes_list = scenes_list[key]
                        break

            if not isinstance(scenes_list, list):
                st.error("O formato do roteiro gerado não é uma lista válida.")
            else:
                total_words = sum(len(scene.get("narration", "").split()) for scene in scenes_list)
                est_seconds = int(total_words / 2.5)  # ~150 palavras por minuto de narração
                st.caption(f"📊 {len(scenes_list)} cena(s) · ⏱️ duração estimada da narração: ~{est_seconds // 60}min {est_seconds % 60}s")

                v = st.session_state.script_version
                anim_options = ["Estática", "Zoom Dinâmico (Zoom In)", "Afastamento Suave (Zoom Out)", "Panorâmica Lateral (Pan)"]

                edited_script = []
                scene_action = None

                for i, scene in enumerate(scenes_list):
                    s_num = scene.get("scene", scene.get("cena", i + 1))
                    s_visual = scene.get("visual", scene.get("imagem", "Descreva o visual aqui"))
                    s_narration = scene.get("narration", scene.get("texto", scene.get("narracao", "")))
                    s_anim = scene.get("animation", "Zoom Dinâmico (Zoom In)")
                    anim_index = anim_options.index(s_anim) if s_anim in anim_options else 1

                    with st.expander(f"#{i + 1} · Cena {s_num}: {s_visual[:50]}...", expanded=True):
                        col_v, col_n, col_a = st.columns([1.5, 2, 1.2])
                        new_visual = col_v.text_input(f"Visual {i}", value=s_visual, key=f"vis_{v}_{i}")
                        new_narration = col_n.text_area(f"Narração {i}", value=s_narration, key=f"nar_{v}_{i}")
                        new_animation = col_a.selectbox(
                            f"Animação {i}",
                            options=anim_options,
                            index=anim_index,
                            key=f"anim_{v}_{i}",
                            help="Selecione a animação perfeita para esta cena."
                        )
                        edited_script.append({
                            "scene": s_num,
                            "visual": new_visual,
                            "narration": new_narration,
                            "animation": new_animation
                        })

                        ctrl_cols = st.columns([1, 1, 1, 6])
                        if ctrl_cols[0].button("⬆️", key=f"up_{v}_{i}", disabled=(i == 0), help="Mover cena para cima", use_container_width=True):
                            scene_action = ("up", i)
                        if ctrl_cols[1].button("⬇️", key=f"down_{v}_{i}", disabled=(i == len(scenes_list) - 1), help="Mover cena para baixo", use_container_width=True):
                            scene_action = ("down", i)
                        if ctrl_cols[2].button("🗑️", key=f"del_{v}_{i}", help="Remover esta cena do roteiro", use_container_width=True):
                            scene_action = ("delete", i)

                if scene_action:
                    action, idx = scene_action
                    if action == "up" and idx > 0:
                        edited_script[idx - 1], edited_script[idx] = edited_script[idx], edited_script[idx - 1]
                    elif action == "down" and idx < len(edited_script) - 1:
                        edited_script[idx + 1], edited_script[idx] = edited_script[idx], edited_script[idx + 1]
                    elif action == "delete":
                        edited_script.pop(idx)

                    st.session_state.script = edited_script
                    st.session_state.script_version += 1
                    if project_name:
                        save_script_to_file(project_name, edited_script)
                    st.rerun()

                st.markdown("---")
                col_add, col_save = st.columns(2)
                with col_add:
                    if st.button("➕ Adicionar Cena", use_container_width=True):
                        next_scene_num = max([s.get("scene", 0) for s in edited_script], default=0) + 1
                        edited_script.append({
                            "scene": next_scene_num,
                            "visual": "Descreva o visual desta nova cena",
                            "narration": "",
                            "animation": "Zoom Dinâmico (Zoom In)"
                        })
                        st.session_state.script = edited_script
                        st.session_state.script_version += 1
                        if project_name:
                            save_script_to_file(project_name, edited_script)
                        st.rerun()
                with col_save:
                    if st.button("💾 Salvar Alterações no Roteiro", use_container_width=True, type="primary"):
                        st.session_state.script = edited_script
                        if project_name:
                            if save_script_to_file(project_name, edited_script):
                                st.success("Alterações salvas e persistidas no histórico com sucesso!")
                            else:
                                st.warning("Alterações salvas em memória, mas houve um erro ao persistir no arquivo.")
                        else:
                            st.success("Alterações salvas com sucesso em memória!")

                st.caption("💡 Remover uma cena não exclui áudios/imagens já gerados para ela do disco. Adicione uma cena novamente com o mesmo número (Cena N) para reaproveitá-los.")

# --- TAB 2: NARRAÇÃO & IMAGENS ---
elif selected == "Narração & Imagens":
    st.header("2. Ativos (Áudio e Imagens)")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🖼️ Imagens do Projeto")
        if not project_name:
            st.warning("⚠️ Insira o nome do projeto/vídeo na barra lateral para liberar as ferramentas de imagem.")
        else:
            # Seletor de destino de download da imagem
            image_target_options = ["Imagem Principal (Global / Fallback)"]
            scene_mapping = {}
            
            if st.session_state.script:
                for idx, scene in enumerate(st.session_state.script):
                    s_num = scene.get("scene", idx + 1)
                    s_vis = scene.get("visual", "Componente")
                    opt_label = f"Cena {s_num}: {s_vis[:35]}..."
                    image_target_options.append(opt_label)
                    scene_mapping[opt_label] = s_num
            
            selected_target_label = st.selectbox(
                "🎯 Destino da Imagem (Onde salvar o download)",
                options=image_target_options,
                index=0,
                help="Escolha se deseja salvar esta imagem como capa global/fallback ou para uma cena específica do roteiro."
            )
            
            target_filename = "main_image.jpg"
            default_query = f"{project_name}"

            if selected_target_label != "Imagem Principal (Global / Fallback)":
                scene_num = scene_mapping[selected_target_label]
                target_filename = f"scene_{scene_num}.jpg"
                for scene in st.session_state.script:
                    if scene.get("scene") == scene_num:
                        default_query = f"{project_name} {scene.get('visual', '')}"
                        break

            # Verificar se a imagem selecionada já existe
            project_assets = save_assets_dir(project_name)
            img_path = os.path.join(project_assets, target_filename)
            image_exists = os.path.exists(img_path)
            
            if image_exists:
                st.success(f"✅ Imagem correspondente ({target_filename}) já está disponível no disco!")
                st.image(img_path, caption=f"Imagem Atual: {selected_target_label}", width=300)
                st.markdown("---")
                st.markdown("#### 🔄 Atualizar ou Buscar Nova Imagem")
            
            show_bgg_tab = (content_type == "Jogos de Tabuleiro & Cartas")
            tab_labels = ["🔍 Busca de Imagens na Web"]
            if show_bgg_tab:
                tab_labels.append("🎲 Board Game Geek (BGG)")
            tab_labels.append("🔗 URL Manual/Scraper")

            inner_tabs = st.tabs(tab_labels)
            inner_tab1 = inner_tabs[0]
            inner_tab_bgg = inner_tabs[1] if show_bgg_tab else None
            inner_tab3 = inner_tabs[-1]

            with inner_tab1:
                st.write("Busque imagens reais relacionadas a esta cena na web:")
                search_query = st.text_input("Termo de Busca de Imagem (ajuste se necessário)", value=default_query, key=f"ddg_search_input_{selected_target_label}")

                with st.expander("🔧 Filtros Avançados (Opcional)"):
                    boost_input = st.text_input(
                        "Palavras-chave para priorizar (separadas por vírgula)",
                        placeholder="Ex: produto, embalagem, foto real",
                        key=f"boost_input_{selected_target_label}"
                    )
                    block_input = st.text_input(
                        "Palavras-chave para evitar (separadas por vírgula)",
                        placeholder="Ex: logo de banco, marca concorrente",
                        key=f"block_input_{selected_target_label}"
                    )

                if st.button("Buscar Imagens na Web", key="web_search_btn"):
                    with st.spinner("Buscando imagens reais na web..."):
                        boost_terms = [t.strip() for t in boost_input.split(",") if t.strip()] if boost_input else None
                        block_terms = [t.strip() for t in block_input.split(",") if t.strip()] if block_input else None
                        results = search_images_web(search_query, max_results=5, boost_terms=boost_terms, block_terms=block_terms)
                        if results:
                            st.session_state.bgg_images = results
                            st.success(f"{len(results)} imagens encontradas!")
                        else:
                            st.error("Nenhuma imagem encontrada. Tente ajustar o termo de busca ou os filtros avançados.")

            if show_bgg_tab:
                with inner_tab_bgg:
                    st.write("Busque a imagem oficial de alta definição direto da base de dados do BGG (apenas para jogos de tabuleiro/cartas):")
                    bgg_input = st.text_input("Link do Jogo ou ID numérico do BGG", placeholder="Ex: 13 ou https://boardgamegeek.com/boardgame/13/catan", key="bgg_search_input")
                    if st.button("Buscar Imagem Oficial no BGG", key="bgg_search_btn"):
                        if bgg_input:
                            with st.spinner("Buscando dados na API do BGG..."):
                                results = get_bgg_game_images(bgg_input)
                                if results:
                                    st.session_state.bgg_images = [{
                                        "title": f"Imagem Oficial do BGG (ID: {bgg_input})",
                                        "main_image": results["main_image"],
                                        "thumbnail": results["thumbnail"]
                                    }]
                                    st.success("Imagem oficial do BGG encontrada com sucesso!")
                                else:
                                    st.error("Não foi possível encontrar imagens para o ID/link no BGG. Verifique e tente novamente.")
                        else:
                            st.error("Por favor, digite o link ou ID do jogo no BGG.")

            with inner_tab3:
                st.write("Extraia imagens de blogs/sites ou configure uma imagem direta por link:")
                manual_url = st.text_input("Cole a URL da página web ou link direto da imagem:", placeholder="https://exemplo.com/pagina-ou-imagem.jpg", key="manual_url_input")
                col_url1, col_url2 = st.columns(2)
                with col_url1:
                    if st.button("🔍 Extrair Imagens da Página", use_container_width=True, key="manual_scrape_btn"):
                        if manual_url:
                            if manual_url.lower().startswith("http"):
                                with st.spinner("Extraindo imagens da página..."):
                                    results = extract_images_from_url(manual_url)
                                    if results:
                                        st.session_state.bgg_images = results
                                        st.success(f"{len(results)} imagens extraídas com sucesso!")
                                    else:
                                        st.error("Nenhuma imagem encontrada na página ou falha ao acessar a URL.")
                            else:
                                st.error("Por favor, digite uma URL válida começando com http:// ou https://")
                        else:
                            st.error("Por favor, insira uma URL.")
                            
                with col_url2:
                    if st.button("🖼️ Usar como Imagem Direta", use_container_width=True, key="manual_direct_btn"):
                        if manual_url:
                            if manual_url.lower().startswith("http"):
                                st.session_state.bgg_images = [{
                                    "title": "URL Direta de Imagem",
                                    "main_image": manual_url,
                                    "thumbnail": manual_url
                                }]
                                st.success("URL direta de imagem configurada! Veja a prévia abaixo.")
                            else:
                                st.error("Por favor, digite uma URL válida começando com http:// ou https://")
                        else:
                            st.error("Por favor, insira uma URL.")
            
            if st.session_state.bgg_images:
                st.divider()
                if isinstance(st.session_state.bgg_images, list):
                    st.write("🔍 **Resultados Encontrados:**")
                    
                    # Grade interativa de imagens em linhas de 5 colunas
                    num_cols = 5
                    for i in range(0, len(st.session_state.bgg_images), num_cols):
                        chunk = st.session_state.bgg_images[i:i+num_cols]
                        cols = st.columns(len(chunk))
                        for idx, img_opt in enumerate(chunk):
                            actual_idx = i + idx
                            with cols[idx]:
                                st.image(img_opt["thumbnail"], caption=f"Opção {actual_idx + 1}", use_container_width=True)
                    
                    selected_idx = st.selectbox(
                        "Escolha a melhor imagem para o vídeo:",
                        range(len(st.session_state.bgg_images)),
                        format_func=lambda x: f"Opção {x + 1} - {st.session_state.bgg_images[x]['title'][:40]}..."
                    )
                    
                    selected_img = st.session_state.bgg_images[selected_idx]
                    st.image(selected_img["main_image"], caption="Visualização Completa", use_container_width=True)
                    
                    if st.button("Confirmar e Baixar para Assets"):
                        with st.spinner("Baixando imagem..."):
                            path = download_image(selected_img["main_image"], project_name, target_filename)
                            if path:
                                st.success(f"Imagem salva com sucesso em: {path}")
                                st.rerun()
                            else:
                                st.error("Erro ao baixar a imagem. Tente outra opção da lista.")
                else:
                    imgs = st.session_state.bgg_images
                    st.image(imgs["main_image"], caption="Imagem Manual Selecionada", use_container_width=True)
                    if st.button("Baixar para Assets"):
                        with st.spinner("Baixando imagem..."):
                            path = download_image(imgs["main_image"], project_name, target_filename)
                            if path:
                                st.success(f"Imagem salva em: {path}")
                                st.rerun()
                            else:
                                st.error("Erro ao baixar a imagem de URL manual.")
            
    with col2:
        st.subheader("🎙️ Narração (TTS)")
        if not st.session_state.script:
            st.warning("⚠️ Gere ou restaure o roteiro na Aba 1 primeiro.")
        else:
            # Verificar status das narrações
            project_assets = save_assets_dir(project_name)
            missing_audios = []
            for scene in st.session_state.script:
                s_num = scene.get("scene", 0)
                audio_path = os.path.join(project_assets, f"scene_{s_num}.mp3")
                if not os.path.exists(audio_path):
                    missing_audios.append(s_num)
            
            if not missing_audios:
                st.success(f"✅ Todos os {len(st.session_state.script)} áudios das cenas já estão gerados no disco!")
            elif len(missing_audios) < len(st.session_state.script):
                st.warning(f"⚠️ {len(st.session_state.script) - len(missing_audios)} de {len(st.session_state.script)} áudios prontos. Cenas pendentes: {', '.join(map(str, missing_audios))}")
            else:
                st.info("ℹ️ Nenhum áudio foi gerado para este projeto ainda.")
                
            st.markdown("---")
            # Seleção de TTS Engine
            tts_engine = st.selectbox(
                "🎙️ Motor de Narração (TTS)",
                ["Edge-TTS (Grátis)", "ElevenLabs (Premium)"],
                index=0,
                help="Edge-TTS é gratuito e extremamente rápido. ElevenLabs fornece vozes neurais ultra-realistas porém requer chave de API."
            )
            
            voice_id = None
            edge_voice = None
            user_api_key = None
            
            if tts_engine == "Edge-TTS (Grátis)":
                edge_voice = st.selectbox(
                    "🗣️ Escolha a Voz (Edge-TTS)",
                    options=["pt-BR-FranciscaNeural", "pt-BR-AntonioNeural", "pt-BR-ThalitaNeural"],
                    format_func=lambda x: {
                        "pt-BR-FranciscaNeural": "Francisca (Feminina)",
                        "pt-BR-AntonioNeural": "Antônio (Masculino)",
                        "pt-BR-ThalitaNeural": "Thalita (Feminina)"
                    }.get(x, x),
                    index=0
                )
            else:
                # ElevenLabs Config
                env_key = os.getenv("ELEVENLABS_API_KEY")
                if not env_key:
                    user_api_key = st.text_input("🔑 ElevenLabs API Key", type="password", help="Cole sua xi-api-key do ElevenLabs.")
                    if not user_api_key:
                        st.warning("⚠️ Insira sua API Key para usar as vozes da ElevenLabs.")
                else:
                    st.success("🔑 Chave ElevenLabs encontrada no arquivo .env!")
                    user_api_key = env_key
                
                voice_option = st.selectbox(
                    "🗣️ Escolha a Voz (ElevenLabs)",
                    options=[
                        "9bwts2yqj2tUf5FB21IV", 
                        "jBpfuIE2acHAzwqMs0g2", 
                        "onwK4e9GkvtGtb5z4kEB", 
                        "custom"
                    ],
                    format_func=lambda x: {
                        "9bwts2yqj2tUf5FB21IV": "Leticia (Feminina - Doce & Clara)",
                        "jBpfuIE2acHAzwqMs0g2": "Gigi (Feminina - Dinâmica & Conversacional)",
                        "onwK4e9GkvtGtb5z4kEB": "Daniel (Masculino - Firme & Profissional)",
                        "custom": "Voz Customizada (Inserir ID...)"
                    }.get(x, x),
                    index=0
                )
                
                if voice_option == "custom":
                    voice_id = st.text_input("ID da Voz Customizada", placeholder="Cole o ID da voz do ElevenLabs aqui")
                else:
                    voice_id = voice_option

            st.write("")
            if st.button("Gerar/Regerar Áudios de Todas as Cenas"):
                if tts_engine == "ElevenLabs (Premium)" and not user_api_key:
                    st.error("Chave de API do ElevenLabs é obrigatória para usar o motor premium.")
                elif tts_engine == "ElevenLabs (Premium)" and voice_option == "custom" and not voice_id:
                    st.error("Por favor, insira o ID da Voz Customizada.")
                else:
                    with st.spinner(f"Gerando narrações em paralelo com {tts_engine}..."):
                        tasks = []
                        for scene in st.session_state.script:
                            s_num = scene.get("scene", 0)
                            text = scene.get("narration", "")
                            audio_path = os.path.join(project_assets, f"scene_{s_num}.mp3")
                            
                            if tts_engine == "ElevenLabs (Premium)":
                                tasks.append({
                                    "text": text,
                                    "path": audio_path,
                                    "engine": "elevenlabs",
                                    "voice_id": voice_id,
                                    "api_key": user_api_key
                                })
                            else:
                                tasks.append({
                                    "text": text,
                                    "path": audio_path,
                                    "engine": "edge-tts",
                                    "voice": edge_voice
                                })
                        
                        from utils import run_generate_multiple_audios
                        success = run_generate_multiple_audios(tasks)
                        if success:
                            st.success(f"Todos os {len(st.session_state.script)} áudios foram gerados com sucesso!")
                        else:
                            st.error("Ocorreu um erro ao gerar os áudios das cenas. Verifique os logs do console.")
                        st.rerun()
            st.info("Os áudios serão usados na renderização final.")

# --- TAB 3: ANIMAÇÃO & VÍDEO FINAL ---
elif selected == "Animação & Vídeo":
    st.header("3. Renderização Final")
    
    if not project_name or not st.session_state.script:
        st.warning("⚠️ Por favor, certifique-se de configurar o nome do projeto/vídeo na barra lateral e gerar o roteiro na Aba 1.")
    else:
        st.subheader("📊 Status dos Ativos do Projeto")
        
        project_assets = save_assets_dir(project_name)
        image_exists = os.path.exists(os.path.join(project_assets, "main_image.jpg"))
        
        missing_audios = []
        scenes_list = st.session_state.script
        for scene in scenes_list:
            s_num = scene.get("scene", 0)
            audio_path = os.path.join(project_assets, f"scene_{s_num}.mp3")
            if not os.path.exists(audio_path):
                missing_audios.append(s_num)
                
        col_img, col_aud = st.columns(2)
        
        with col_img:
            st.write("🖼️ **Status das Imagens:**")
            if image_exists:
                st.success("✅ Imagem Principal (`main_image.jpg` pronta)")
            else:
                st.warning("⚠️ Imagem Principal (`main_image.jpg` ausente - use como fallback geral)")
                
            # Scan scene-specific images
            scene_images_status = []
            for scene in scenes_list:
                s_num = scene.get("scene", 0)
                s_vis = scene.get("visual", "Visual")
                found_img = False
                for ext in ["jpg", "png", "jpeg"]:
                    if os.path.exists(os.path.join(project_assets, f"scene_{s_num}.{ext}")):
                        found_img = True
                        break
                scene_images_status.append((s_num, s_vis, found_img))
                
            missing_scene_imgs = [num for num, _, found in scene_images_status if not found]
            
            if not missing_scene_imgs:
                st.success("✅ Todas as cenas possuem imagens específicas correspondentes!")
            elif len(missing_scene_imgs) < len(scenes_list):
                st.info(f"ℹ️ {len(scenes_list) - len(missing_scene_imgs)} de {len(scenes_list)} cenas têm imagens próprias. As pendentes usarão a Imagem Principal.")
                with st.expander("🔍 Verificar Mapeamento das Cenas"):
                    for num, vis, found in scene_images_status:
                        icon = "✅ Pronta" if found else "ℹ️ Usará Fallback"
                        st.markdown(f"* **Cena {num}:** {icon} — *{vis[:35]}*")
            else:
                st.info("ℹ️ Nenhuma cena possui imagem específica ainda (todas usarão a Imagem Principal como fallback).")
                
        with col_aud:
            st.write("🎙️ **Narrações das Cenas (Áudio):**")
            if not missing_audios:
                st.success(f"✅ Todos os {len(scenes_list)} áudios foram gerados!")
            else:
                st.error(f"❌ Ausente ({len(missing_audios)} de {len(scenes_list)} áudios não encontrados)")
                st.write(f"Cenas com áudio em falta: {', '.join(map(str, missing_audios))}")
                st.caption("Acesse a **Aba 2** e clique em 'Gerar Áudios de Todas as Cenas' para gerá-los.")
        
        st.divider()
        st.subheader("🎬 Configurações de Renderização")

        col_style, col_music = st.columns(2)

        with col_style:
            visual_style = st.selectbox(
                "🎨 Estilo Visual do Vídeo",
                ["Clássico", "Gradiente Moderno", "Neon Dark"],
                index=0,
                help="Define o layout visual, borda e fundo do vídeo vertical."
            )

            animation_type = st.selectbox(
                "🎬 Animação de Cenas (Efeito Câmera)",
                ["Contextual (Definido no Roteiro)", "Estática", "Zoom Dinâmico (Zoom In)", "Afastamento Suave (Zoom Out)", "Panorâmica Lateral (Pan)"],
                index=0,
                help="Escolha 'Contextual' para usar as animações individuais geradas pela IA por cena no roteiro, ou force um estilo fixo global."
            )

        with col_music:
            bg_music_options = ["Sem Música", "Aleatória"]
            bg_music_dir = os.path.join("assets", "bg_music")

            # Garante que a pasta existe e baixa se necessário para mostrar na lista
            from utils import ensure_default_bg_music
            ensure_default_bg_music()

            if os.path.exists(bg_music_dir):
                mp3_files = sorted([f for f in os.listdir(bg_music_dir) if f.endswith(".mp3")])
                bg_music_options.extend(mp3_files)

            bg_music_name = st.selectbox(
                "🎵 Música de Fundo (BGM)",
                options=bg_music_options,
                index=0,
                format_func=lambda x: x.replace(".mp3", "").replace("_", " ").title() if x not in ["Sem Música", "Aleatória"] else x,
                help="Selecione a trilha sonora de fundo livre de direitos autorais."
            )

        bg_volume = 0.15
        if bg_music_name != "Sem Música":
            bg_volume_percent = st.slider(
                "🔊 Volume da Música de Fundo",
                min_value=0,
                max_value=50,
                value=15,
                step=5,
                format="%d%%",
                help="Recomendado manter entre 10% e 20% para não sobrepor a narração."
            )
            bg_volume = bg_volume_percent / 100.0

        st.divider()
        st.subheader("👁️ Pré-visualização do Estilo")
        st.caption("Gere uma prévia instantânea do frame com o estilo, a imagem e a legenda da cena escolhida — sem esperar pela renderização completa do vídeo.")

        preview_options = {}
        for idx, scene in enumerate(scenes_list):
            s_num = scene.get("scene", idx + 1)
            s_vis = scene.get("visual", "Cena")
            preview_options[f"Cena {s_num}: {s_vis[:40]}"] = scene

        col_prev_sel, col_prev_btn = st.columns([3, 1])
        with col_prev_sel:
            preview_label = st.selectbox("Cena para pré-visualizar", options=list(preview_options.keys()), key="preview_scene_select")
        with col_prev_btn:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            generate_preview = st.button("🖼️ Gerar Prévia", use_container_width=True)

        if generate_preview:
            preview_scene = preview_options[preview_label]
            preview_num = preview_scene.get("scene", 0)

            preview_img_path = None
            for ext in ["jpg", "png", "jpeg"]:
                candidate = os.path.join(project_assets, f"scene_{preview_num}.{ext}")
                if os.path.exists(candidate):
                    preview_img_path = candidate
                    break
            if not preview_img_path and image_exists:
                preview_img_path = os.path.join(project_assets, "main_image.jpg")

            if not preview_img_path:
                st.error("Nenhuma imagem disponível para esta cena. Baixe ao menos a Imagem Principal na Aba 2 antes de gerar a prévia.")
            else:
                with st.spinner("Renderizando prévia do frame..."):
                    preview_frame_path = create_scene_frame(preview_img_path, preview_scene.get("narration", ""), preview_num, project_name, visual_style=visual_style)
                    if preview_frame_path and os.path.exists(preview_frame_path):
                        with open(preview_frame_path, "rb") as f:
                            preview_bytes = f.read()
                        os.remove(preview_frame_path)
                        st.image(preview_bytes, caption=f"Prévia • Estilo: {visual_style}", width=340)
                    else:
                        st.error("Não foi possível gerar a prévia do frame.")

        st.caption("💡 As **Animações Contextuais Semânticas de Câmera** (Ken Burns) são aplicadas automaticamente na renderização final, a custo zero de API.")

        st.divider()
        st.subheader("🎬 Exportar MP4")
        
        # Verify if we have at least one valid fallback image or specific images for all scenes
        all_scenes_have_images = True
        for scene in scenes_list:
            s_num = scene.get("scene", 0)
            has_scene_img = False
            for ext in ["jpg", "png", "jpeg"]:
                if os.path.exists(os.path.join(project_assets, f"scene_{s_num}.{ext}")):
                    has_scene_img = True
                    break
            if not has_scene_img:
                all_scenes_have_images = False
                break
                
        can_render_images = image_exists or all_scenes_have_images
        
        if not can_render_images or missing_audios:
            st.error("⚠️ Para renderizar o vídeo final, certifique-se de baixar ao menos a Imagem Principal (ou todas as imagens por cena) e gerar os áudios na Aba 2.")
            st.button("Renderizar Vídeo Vertical (9:16)", disabled=True, key="render_btn_disabled")
        else:
            st.success("🎉 Todos os ativos cruciais foram validados! Pronto para compilar o vídeo final.")
            
            video_output = os.path.join(project_assets, "video_final.mp4")
            
            if st.button("Renderizar Vídeo Vertical (9:16)"):
                with st.spinner("Renderizando vídeo vertical premium com MoviePy e Pillow... Isso pode levar de 15 a 30 segundos."):
                    video_path = render_video(
                        project_name, 
                        st.session_state.script, 
                        visual_style=visual_style, 
                        bg_music_name=bg_music_name, 
                        bg_volume=bg_volume,
                        animation_type=animation_type
                    )
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
                        file_name=f"{project_name.lower().replace(' ', '_')}_video_final.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )

# --- TAB 4: CLIPES (MONTAGEM LIVRE) ---
elif selected == "Clipes":
    st.header("4. 🎞️ Montagem de Clipes")
    st.markdown("Arraste e solte clipes de vídeo para montar uma edição personalizada, sem depender do roteiro gerado.")

    if not project_name:
        st.warning("⚠️ Defina o nome do projeto na barra lateral antes de continuar.")
    else:
        # ── Upload de clipes ──────────────────────────────────────────────
        st.subheader("📁 Biblioteca de Clipes")
        uploaded_clips = st.file_uploader(
            "Envie um ou mais clipes de vídeo",
            type=["mp4", "mov", "webm", "avi", "mkv", "m4v"],
            accept_multiple_files=True,
            key="clip_uploader",
        )
        if uploaded_clips:
            with st.spinner("Salvando e analisando clipes…"):
                for uf in uploaded_clips:
                    save_video_clip(uf.read(), uf.name, project_name)
            st.success(f"✅ {len(uploaded_clips)} clipe(s) adicionado(s) à biblioteca.")
            st.rerun()

        clips_on_disk = list_project_clips(project_name)

        if not clips_on_disk:
            st.info("Nenhum clipe na biblioteca. Envie arquivos acima para começar.")
        else:
            # ── Reordenação com drag-and-drop (ou fallback manual) ────────
            try:
                from streamlit_sortables import sort_items
                if "clip_order" not in st.session_state or set(st.session_state.clip_order) != set(clips_on_disk):
                    st.session_state.clip_order = clips_on_disk[:]
                st.markdown("**Arraste os clipes para definir a ordem de montagem:**")
                sorted_order = sort_items(st.session_state.clip_order, direction="vertical")
                st.session_state.clip_order = sorted_order
                ordered_clips = sorted_order
            except ImportError:
                st.info("💡 Instale `streamlit-sortables` para arrastar e soltar. Use os campos abaixo para ordenar manualmente.")
                if "clip_order" not in st.session_state or set(st.session_state.clip_order) != set(clips_on_disk):
                    st.session_state.clip_order = clips_on_disk[:]
                ordered_clips = st.session_state.clip_order[:]

            # ── Grade de thumbnails ───────────────────────────────────────
            st.markdown("---")
            st.markdown("**Clipes na biblioteca:**")
            grid_cols = st.columns(min(len(clips_on_disk), 4))
            for ci, fname in enumerate(clips_on_disk):
                info = get_clip_info(project_name, fname)
                with grid_cols[ci % 4]:
                    if info.get("thumbnail"):
                        st.image(info["thumbnail"], use_container_width=True)
                    else:
                        st.markdown("🎬 *(sem preview)*")
                    dur = info.get("duration", 0)
                    st.caption(f"**{fname}**  \n⏱ {dur:.1f}s")
                    if st.button("🗑️ Remover", key=f"del_clip_{fname}"):
                        delete_video_clip(project_name, fname)
                        if fname in st.session_state.get("clip_order", []):
                            st.session_state.clip_order.remove(fname)
                        st.rerun()

            # ── Configurações por clipe ───────────────────────────────────
            st.markdown("---")
            st.subheader("⚙️ Configurações por Clipe")
            clip_configs = {}
            for fname in ordered_clips:
                info = get_clip_info(project_name, fname)
                raw_dur = info.get("duration", 0)
                with st.expander(f"🎬 {fname}  •  ⏱ {raw_dur:.1f}s", expanded=False):
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        start_t = st.number_input(
                            "Início (s)", min_value=0.0,
                            max_value=max(0.0, raw_dur - 0.1),
                            value=0.0, step=0.1,
                            key=f"clip_start_{fname}",
                        )
                    with c2:
                        end_t = st.number_input(
                            "Fim (s)", min_value=0.1,
                            max_value=raw_dur if raw_dur > 0 else 999.0,
                            value=raw_dur if raw_dur > 0 else 10.0, step=0.1,
                            key=f"clip_end_{fname}",
                        )
                    with c3:
                        vol = st.slider(
                            "Volume do clipe", 0.0, 2.0, 1.0, 0.05,
                            key=f"clip_vol_{fname}",
                        )
                    caption_text = st.text_input(
                        "Legenda sobreposta (opcional)", value="",
                        key=f"clip_caption_{fname}",
                    )
                    clip_configs[fname] = {
                        "start": start_t,
                        "end": end_t,
                        "volume": vol,
                        "caption": caption_text,
                    }

            # ── Configurações de saída ────────────────────────────────────
            st.markdown("---")
            st.subheader("🎛️ Configurações de Saída")
            co1, co2, co3 = st.columns(3)
            with co1:
                fmt = st.selectbox(
                    "Formato de Saída",
                    ["Vertical 9:16 (TikTok/Reels)", "Horizontal 16:9 (YouTube)", "Quadrado 1:1 (Feed)"],
                    index=0,
                    key="clip_format",
                )
                fmt_map = {
                    "Vertical 9:16 (TikTok/Reels)": (1080, 1920),
                    "Horizontal 16:9 (YouTube)": (1920, 1080),
                    "Quadrado 1:1 (Feed)": (1080, 1080),
                }
                output_size = fmt_map[fmt]
            with co2:
                transition = st.selectbox(
                    "Transição entre Clipes",
                    ["Corte Seco", "Fade to Black"],
                    index=0,
                    key="clip_transition",
                )
            with co3:
                transition_dur = st.slider(
                    "Duração da Transição (s)", 0.1, 1.5, 0.5, 0.1,
                    key="clip_transition_dur",
                    disabled=(transition == "Corte Seco"),
                )

            # BGM
            bg_dir = os.path.join("assets", "bg_music")
            music_options = ["Sem Música", "Aleatória"]
            if os.path.exists(bg_dir):
                music_options += sorted([f for f in os.listdir(bg_dir) if f.endswith(".mp3")])
            cm1, cm2 = st.columns([2, 1])
            with cm1:
                bg_music_name = st.selectbox("🎵 Música de Fundo (BGM)", music_options, index=0, key="clip_bgm")
            with cm2:
                bg_vol = st.slider("Volume BGM", 0.0, 0.5, 0.15, 0.01, key="clip_bgm_vol",
                                   disabled=(bg_music_name == "Sem Música"))

            # Summary
            total_dur = sum(
                clip_configs.get(f, {}).get("end", get_clip_info(project_name, f).get("duration", 0)) -
                clip_configs.get(f, {}).get("start", 0.0)
                for f in ordered_clips
            )
            st.info(f"📊 **{len(ordered_clips)} clipe(s)** · ⏱ duração estimada: **{total_dur:.1f}s**")

            st.markdown("---")
            if st.button("🎬 Montar Vídeo Final", type="primary", use_container_width=True, key="btn_assemble"):
                with st.spinner("Montando vídeo… isso pode levar alguns minutos dependendo do tamanho dos clipes."):
                    result_path = assemble_clips(
                        project_name=project_name,
                        ordered_clips=ordered_clips,
                        clip_configs=clip_configs,
                        bg_music_name=bg_music_name,
                        bg_volume=bg_vol,
                        output_size=output_size,
                        transition=transition,
                        transition_duration=transition_dur,
                    )
                if result_path and os.path.exists(result_path):
                    st.success("✅ Vídeo montado com sucesso!")
                    st.session_state["clip_result_path"] = result_path
                else:
                    st.error("❌ Falha na montagem. Verifique o console para detalhes.")

            if st.session_state.get("clip_result_path") and os.path.exists(st.session_state["clip_result_path"]):
                result_path = st.session_state["clip_result_path"]
                st.video(result_path)
                with open(result_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Baixar Vídeo Montado (MP4)",
                        data=f,
                        file_name=f"{project_name.lower().replace(' ', '_')}_montagem.mp4",
                        mime="video/mp4",
                        use_container_width=True,
                    )

# --- TAB 5: METADADOS SOCIAIS (COPYWRITER) ---
elif selected == "Metadados Sociais":
    st.header("4. Metadados Sociais (Copywriter IA)")
    
    if not project_name or not st.session_state.script:
        st.warning("⚠️ Certifique-se de configurar o nome do projeto/vídeo na barra lateral e gerar o roteiro na Aba 1 primeiro.")
    else:
        st.write("Gere copys otimizadas de postagem (legenda, títulos e hashtags) para o TikTok, Reels e Shorts com base no roteiro atual:")
        
        # Verificar se já existem metadados salvos
        project_assets = save_assets_dir(project_name)
        metadata_json_path = os.path.join(project_assets, "metadata.json")
        metadata_txt_path = os.path.join(project_assets, "metadata.txt")
        
        saved_metadata = None
        if os.path.exists(metadata_json_path):
            try:
                with open(metadata_json_path, "r", encoding="utf-8") as f:
                    saved_metadata = json.load(f)
            except Exception:
                pass
                
        if saved_metadata:
            st.success("✅ Metadados sociais carregados do disco!")
        else:
            st.info("ℹ️ Nenhum metadado gerado para este projeto ainda.")

        if st.button("Gerar Metadados Sociais com IA", type="primary"):
            with st.spinner("Analisando roteiro e escrevendo copies de alta conversão..."):
                result = generate_social_metadata(project_name, st.session_state.script, content_type)
                if isinstance(result, dict) and "error" not in result:
                    st.success("🎉 Metadados sociais gerados e salvos com sucesso!")
                    st.rerun()
                elif isinstance(result, dict) and "error" in result:
                    st.error(f"Erro ao gerar metadados: {result['error']}")
                else:
                    st.error("Erro inesperado ao gerar metadados.")
                    
        if saved_metadata:
            st.divider()
            
            # Títulos sugeridos
            st.subheader("💡 Opções de Títulos (Capas / Headlines)")
            for i, title in enumerate(saved_metadata.get("titles", [])):
                st.code(title, language="")
                
            # Copies de legenda
            st.subheader("📝 Copies e Legendas de Postagem")
            captions = saved_metadata.get("captions", [])
            
            col_cap1, col_cap2 = st.columns(2)
            with col_cap1:
                st.markdown("**Opção 1: Direta e Focada em Engajamento Rápido (TikTok)**")
                legenda_1 = captions[0] if len(captions) > 0 else ""
                new_legenda_1 = st.text_area("Legenda TikTok", value=legenda_1, height=200, key="leg_tk")
            with col_cap2:
                st.markdown("**Opção 2: Narrativa com Gancho e CTA Forte (Instagram/Reels)**")
                legenda_2 = captions[1] if len(captions) > 1 else ""
                new_legenda_2 = st.text_area("Legenda Reels", value=legenda_2, height=200, key="leg_ig")
                
            # Hashtags
            st.subheader("🏷️ Hashtags de Nicho Recomendadas")
            hashtags = saved_metadata.get("hashtags", "")
            new_hashtags = st.text_area("Hashtags", value=hashtags, height=100, key="hash")
            
            # Botão para salvar alterações manuais
            if st.button("Salvar Alterações Manuais nos Metadados"):
                updated_data = {
                    "titles": saved_metadata.get("titles", []),
                    "captions": [new_legenda_1, new_legenda_2],
                    "hashtags": new_hashtags
                }
                
                try:
                    with open(metadata_json_path, "w", encoding="utf-8") as f:
                        json.dump(updated_data, f, ensure_ascii=False, indent=4)
                        
                    with open(metadata_txt_path, "w", encoding="utf-8") as f:
                        f.write("=== TÍTULOS SUGERIDOS ===\n")
                        for idx, t in enumerate(updated_data.get("titles", [])):
                            f.write(f"{idx+1}. {t}\n")
                        f.write(f"\n=== LEGENDA 1 (TikTok) ===\n{new_legenda_1}\n")
                        f.write(f"\n=== LEGENDA 2 (Instagram/Reels) ===\n{new_legenda_2}\n")
                        f.write(f"\n=== HASHTAGS ===\n{new_hashtags}\n")
                        
                    st.success("Alterações salvas com sucesso no disco!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar alterações: {e}")
                    
            # Opção de download rápido do arquivo final formatado
            if os.path.exists(metadata_txt_path):
                with open(metadata_txt_path, "r", encoding="utf-8") as f:
                    txt_data = f.read()
                    
                st.download_button(
                    label="📥 Baixar Metadados Completos (metadata.txt)",
                    data=txt_data,
                    file_name=f"{project_name.lower().replace(' ', '_')}_metadata.txt",
                    mime="text/plain",
                    use_container_width=True
                )

# --- SIDEBAR ATIVOS ---
if project_name:
    st.sidebar.markdown("---")
    with st.sidebar.expander("🗑️ Limpeza de Ativos"):
        st.write("Exclua arquivos indesejados deste projeto:")
        
        # Granular asset deletion
        if st.button("🎙️ Excluir Áudios/Cenas", use_container_width=True):
            if delete_project_assets(project_name, "audio"):
                st.success("Áudios e cenas excluídos!")
                st.rerun()
            else:
                st.info("Nenhum áudio para excluir.")
                
        if st.button("🖼️ Excluir Imagem Principal", use_container_width=True):
            if delete_project_assets(project_name, "image"):
                st.success("Imagem principal excluída!")
                st.rerun()
            else:
                st.info("Nenhuma imagem para excluir.")
                
        if st.button("🎬 Excluir Vídeo Final", use_container_width=True):
            if delete_project_assets(project_name, "video"):
                st.success("Vídeo final excluído!")
                st.rerun()
            else:
                st.info("Nenhum vídeo para excluir.")
                
        if st.button("📝 Excluir Roteiro (JSON)", use_container_width=True):
            dest_dir = save_assets_dir(project_name)
            script_path = os.path.join(dest_dir, "script.json")
            if os.path.exists(script_path):
                os.remove(script_path)
                st.session_state.script = None
                st.success("Roteiro excluído do disco!")
                st.rerun()
            else:
                st.info("Nenhum roteiro salvo encontrado.")
                
        st.markdown("---")
        # Extreme caution action
        if st.button("🚨 Excluir Todo o Projeto", use_container_width=True, type="primary"):
            if delete_project_assets(project_name, "all"):
                st.success(f"Projeto '{project_name}' removido por completo!")
                st.session_state.project_name_val = ""
                st.session_state.loaded_project_name = None
                st.session_state.script = None
                st.session_state.bgg_images = None
                st.rerun()
            else:
                st.error("Erro ao deletar diretório.")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("Fábrica Autônoma de Vídeos 🤖")
