import streamlit as st
import os
import json
from utils import extract_text_from_pdf, generate_script, save_assets_dir, get_bgg_game_images, download_image, run_generate_audio, search_game_images_ddg, render_video, save_script_to_file, load_script_from_file, extract_images_from_url, delete_game_assets, generate_social_metadata
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


# Initialize session state for script and game data
if "script" not in st.session_state:
    st.session_state.script = None
if "game_path" not in st.session_state:
    st.session_state.game_path = None
if "bgg_images" not in st.session_state:
    st.session_state.bgg_images = None
if "game_name_val" not in st.session_state:
    st.session_state.game_name_val = ""
if "loaded_game_name" not in st.session_state:
    st.session_state.loaded_game_name = None
if "last_history_select" not in st.session_state:
    st.session_state.last_history_select = ""

# --- SIDEBAR (Configurações) ---
st.sidebar.title("⚙️ Configurações")

# Histórico de jogos salvos em assets/
existing_games = [""]
if os.path.exists("assets"):
    folders = sorted([f for f in os.listdir("assets") if os.path.isdir(os.path.join("assets", f))])
    existing_games.extend(folders)

selected_history = st.sidebar.selectbox(
    "📂 Restaurar Jogo Existente",
    options=existing_games,
    index=0,
    format_func=lambda x: "Selecione um jogo..." if x == "" else x.replace("_", " ").title(),
    key="history_select"
)

# Atualizar o valor de busca/nome do jogo a partir da escolha do histórico (apenas quando houver mudança real de seleção)
if st.session_state.history_select != st.session_state.last_history_select:
    st.session_state.last_history_select = st.session_state.history_select
    if st.session_state.history_select != "":
        game_name_from_history = st.session_state.history_select.replace("_", " ").title()
        st.session_state.game_name_val = game_name_from_history
        st.session_state.game_name_input = game_name_from_history

game_name = st.sidebar.text_input(
    "Nome do Jogo", 
    value=st.session_state.game_name_val,
    placeholder="Ex: Catan, Azul, Dixit...",
    key="game_name_input"
)
st.session_state.game_name_val = game_name

# Carregar o script.json automaticamente na troca de jogo
if game_name != st.session_state.loaded_game_name:
    st.session_state.loaded_game_name = game_name
    if game_name:
        st.session_state.game_path = save_assets_dir(game_name)
        loaded_script = load_script_from_file(game_name)
        if loaded_script:
            st.session_state.script = loaded_script
            st.sidebar.info(f"📂 Roteiro de '{game_name}' carregado do histórico!")
        else:
            st.session_state.script = None
            st.session_state.bgg_images = None
    else:
        st.session_state.script = None
        st.session_state.bgg_images = None

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
st.markdown("<div style='text-align: center; margin-top: 1.5rem;'>", unsafe_allow_html=True)
st.title("🎬 Fábrica Autônoma de Vídeos Didáticos")
st.markdown("<p style='font-size: 19px; color: #94A3B8; margin-top: 0px;'>Transforme manuais de jogos em vídeos verticais premium para redes sociais.</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# Elegant Horizontal Navigation Menu
selected = option_menu(
    menu_title=None,
    options=["Roteiro", "Narração & Imagens", "Animação & Vídeo", "Metadados Sociais"],
    icons=["pencil-square", "mic", "play-btn", "rocket-takeoff"],
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
elif selected == "Metadados Sociais":
    step_idx = 3

sac.steps(
    items=[
        sac.StepsItem(title='Roteiro', subtitle='Upload & Edição'),
        sac.StepsItem(title='Ativos', subtitle='Locução & Imagem'),
        sac.StepsItem(title='Renderização', subtitle='Efeitos & Vídeo'),
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
    if not game_name or (not manual_file and not st.session_state.script):
        st.warning("⚠️ Por favor, preencha o nome do jogo e faça o upload do manual na barra lateral para gerar um roteiro.")
    else:
        if st.session_state.script:
            st.info(f"Roteiro carregado para o jogo: **{game_name}**")
        else:
            st.info(f"Pronto para processar o jogo: **{game_name}**")
        
        if st.button("Gerar Roteiro com IA"):
            if not manual_file:
                st.error("Por favor, faça o upload de um arquivo manual em PDF para gerar o roteiro.")
            else:
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
                        if game_name:
                            save_script_to_file(game_name, st.session_state.script)
                        st.success("Roteiro gerado e persistido no histórico com sucesso!")
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
                    s_anim = scene.get("animation", "Zoom Dinâmico (Zoom In)")
                    
                    anim_options = ["Estática", "Zoom Dinâmico (Zoom In)", "Afastamento Suave (Zoom Out)", "Panorâmica Lateral (Pan)"]
                    anim_index = anim_options.index(s_anim) if s_anim in anim_options else 1
                    
                    with st.expander(f"Cena {s_num}: {s_visual[:50]}...", expanded=True):
                        col_v, col_n, col_a = st.columns([1.5, 2, 1.2])
                        new_visual = col_v.text_input(f"Visual {i}", value=s_visual, key=f"vis_{i}")
                        new_narration = col_n.text_area(f"Narração {i}", value=s_narration, key=f"nar_{i}")
                        new_animation = col_a.selectbox(
                            f"Animação {i}",
                            options=anim_options,
                            index=anim_index,
                            key=f"anim_{i}",
                            help="Selecione a animação perfeita para esta cena."
                        )
                        edited_script.append({
                            "scene": s_num,
                            "visual": new_visual,
                            "narration": new_narration,
                            "animation": new_animation
                        })
                
                if st.button("Salvar Alterações no Roteiro"):
                    st.session_state.script = edited_script
                    if game_name:
                        if save_script_to_file(game_name, edited_script):
                            st.success("Alterações salvas e persistidas no histórico com sucesso!")
                        else:
                            st.warning("Alterações salvas em memória, mas houve um erro ao persistir no arquivo.")
                    else:
                        st.success("Alterações salvas com sucesso em memória!")

# --- TAB 2: NARRAÇÃO & IMAGENS ---
elif selected == "Narração & Imagens":
    st.header("2. Ativos (Áudio e Imagens)")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🖼️ Imagens do Jogo")
        if not game_name:
            st.warning("⚠️ Insira o nome do jogo na barra lateral para liberar as ferramentas de imagem.")
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
            
            target_filename = "main_game.jpg"
            default_query = f"{game_name} board game"
            
            if selected_target_label != "Imagem Principal (Global / Fallback)":
                scene_num = scene_mapping[selected_target_label]
                target_filename = f"scene_{scene_num}.jpg"
                for scene in st.session_state.script:
                    if scene.get("scene") == scene_num:
                        default_query = f"{game_name} {scene.get('visual', '')} board game"
                        break

            # Verificar se a imagem selecionada já existe
            game_assets = save_assets_dir(game_name)
            img_path = os.path.join(game_assets, target_filename)
            image_exists = os.path.exists(img_path)
            
            if image_exists:
                st.success(f"✅ Imagem correspondente ({target_filename}) já está disponível no disco!")
                st.image(img_path, caption=f"Imagem Atual: {selected_target_label}", width=300)
                st.markdown("---")
                st.markdown("#### 🔄 Atualizar ou Buscar Nova Imagem")
            
            inner_tab1, inner_tab2, inner_tab3 = st.tabs([
                "🔍 Busca Web DDG", 
                "🎲 API Oficial BGG", 
                "🔗 URL Manual/Scraper"
            ])
            
            with inner_tab1:
                st.write("Busque imagens de componentes e tabuleiros na web:")
                search_query = st.text_input("Termo de Busca de Imagem (ajuste se necessário)", value=default_query, key=f"ddg_search_input_{selected_target_label}")
                if st.button("Buscar Imagens na Web", key="ddg_search_btn"):
                    with st.spinner("Buscando imagens reais na web..."):
                        results = search_game_images_ddg(search_query, max_results=5)
                        if results:
                            st.session_state.bgg_images = results
                            st.success(f"{len(results)} imagens encontradas!")
                        else:
                            st.error("Nenhuma imagem encontrada. Tente ajustar o termo de busca ou use a API oficial do BGG.")
                            
            with inner_tab2:
                st.write("Busque a imagem oficial de alta definição direto da base de dados do BGG:")
                bgg_input = st.text_input("Link do Jogo ou ID numérico do BGG", placeholder="Ex: 13 ou https://boardgamegeek.com/boardgame/13/catan", key="bgg_search_input")
                if st.button("Buscar Imagem Oficial no BGG", key="bgg_search_btn"):
                    if bgg_input:
                        with st.spinner("Buscando dados na API do BGG..."):
                            from utils import get_bgg_game_images
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
                        st.error("Por favor, digite o Link ou ID do jogo no BGG.")
                        
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
                            path = download_image(selected_img["main_image"], game_name, target_filename)
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
                            path = download_image(imgs["main_image"], game_name, target_filename)
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
            game_assets = save_assets_dir(game_name)
            missing_audios = []
            for scene in st.session_state.script:
                s_num = scene.get("scene", 0)
                audio_path = os.path.join(game_assets, f"scene_{s_num}.mp3")
                if not os.path.exists(audio_path):
                    missing_audios.append(s_num)
            
            if not missing_audios:
                st.success(f"✅ Todos os {len(st.session_state.script)} áudios das cenas já estão gerados no disco!")
            elif len(missing_audios) < len(st.session_state.script):
                st.warning(f"⚠️ {len(st.session_state.script) - len(missing_audios)} de {len(st.session_state.script)} áudios prontos. Cenas pendentes: {', '.join(map(str, missing_audios))}")
            else:
                st.info("ℹ️ Nenhum áudio foi gerado para este jogo ainda.")
                
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
                            audio_path = os.path.join(game_assets, f"scene_{s_num}.mp3")
                            
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
            st.write("🖼️ **Status das Imagens:**")
            if image_exists:
                st.success("✅ Imagem Principal (`main_game.jpg` pronta)")
            else:
                st.warning("⚠️ Imagem Principal (`main_game.jpg` ausente - use como fallback geral)")
                
            # Scan scene-specific images
            scene_images_status = []
            for scene in scenes_list:
                s_num = scene.get("scene", 0)
                s_vis = scene.get("visual", "Visual")
                found_img = False
                for ext in ["jpg", "png", "jpeg"]:
                    if os.path.exists(os.path.join(game_assets, f"scene_{s_num}.{ext}")):
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
        st.subheader("📹 Efeitos de Vídeo por IA (Image-to-Video)")
        
        with st.container():
            st.markdown("""
            <div style="background: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.2); border-radius: 12px; padding: 1.2rem; margin-bottom: 1.5rem;">
                <h4 style="color: #818CF8; margin-top: 0px; margin-bottom: 0.5rem; font-family: Outfit, sans-serif; font-size: 16px;">🤖 Animação 3D Generativa de Componentes (Opcional - Fase 3.1)</h4>
                <p style="font-size: 13.5px; color: #94A3B8; margin-bottom: 0px; line-height: 1.55;">
                    Esta ferramenta opcional integra APIs externas de inteligência artificial geradora de vídeo (como <strong>Kling AI</strong>, <strong>Luma Dream Machine</strong> ou <strong>Runway Gen-3</strong>) para converter as imagens estáticas dos seus componentes em clipes de vídeo 3D de 4 segundos.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Form to insert Luma / Kling Key if they want to integrate in the future
            col_api, col_act = st.columns([2.5, 1])
            with col_api:
                kling_key = st.text_input("🔑 Chave de API Kling / Luma (Opcional)", type="password", placeholder="Insira sua API Key para ativar o gerador 3D...", key="kling_api_key")
            with col_act:
                # Add vertical spacing
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                if kling_key:
                    if st.button("🎬 Gerar Vídeos 3D via API", type="primary", use_container_width=True):
                        st.info("Conectando à API generativa...")
                else:
                    st.button("⚙️ Motor Inativo", disabled=True, use_container_width=True)
            
            st.markdown("<p style='font-size: 13px; color: #64748B; font-style: italic; margin-top: 8px;'>💡 Nota: As <strong>Animações Contextuais Semânticas de Câmera</strong> (Ken Burns de Alto Padrão) já estão ativas e rodando localmente a <strong>custo zero de API</strong> nas configurações de renderização abaixo!</p>", unsafe_allow_html=True)
            
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
        st.subheader("🎬 Exportar MP4")
        
        # Verify if we have at least one valid fallback image or specific images for all scenes
        all_scenes_have_images = True
        for scene in scenes_list:
            s_num = scene.get("scene", 0)
            has_scene_img = False
            for ext in ["jpg", "png", "jpeg"]:
                if os.path.exists(os.path.join(game_assets, f"scene_{s_num}.{ext}")):
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
            
            video_output = os.path.join(game_assets, "video_final.mp4")
            
            if st.button("Renderizar Vídeo Vertical (9:16)"):
                with st.spinner("Renderizando vídeo vertical premium com MoviePy e Pillow... Isso pode levar de 15 a 30 segundos."):
                    video_path = render_video(
                        game_name, 
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
                        file_name=f"{game_name.lower().replace(' ', '_')}_video_final.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )

# --- TAB 4: METADADOS SOCIAIS (COPYWRITER) ---
elif selected == "Metadados Sociais":
    st.header("4. Metadados Sociais (Copywriter IA)")
    
    if not game_name or not st.session_state.script:
        st.warning("⚠️ Certifique-se de configurar o nome do jogo na barra lateral e gerar o roteiro na Aba 1 primeiro.")
    else:
        st.write("Gere copys otimizadas de postagem (legenda, títulos e hashtags) para o TikTok, Reels e Shorts com base no roteiro atual:")
        
        # Verificar se já existem metadados salvos
        game_assets = save_assets_dir(game_name)
        metadata_json_path = os.path.join(game_assets, "metadata.json")
        metadata_txt_path = os.path.join(game_assets, "metadata.txt")
        
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
            st.info("ℹ️ Nenhum metadado gerado para este jogo ainda.")
            
        if st.button("Gerar Metadados Sociais com IA", type="primary"):
            with st.spinner("Analisando roteiro e escrevendo copies de alta conversão..."):
                result = generate_social_metadata(game_name, st.session_state.script)
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
                    file_name=f"{game_name.lower().replace(' ', '_')}_metadata.txt",
                    mime="text/plain",
                    use_container_width=True
                )

# --- SIDEBAR ATIVOS ---
if game_name:
    st.sidebar.markdown("---")
    with st.sidebar.expander("🗑️ Limpeza de Ativos"):
        st.write("Exclua arquivos indesejados deste jogo:")
        
        # Granular asset deletion
        if st.button("🎙️ Excluir Áudios/Cenas", use_container_width=True):
            if delete_game_assets(game_name, "audio"):
                st.success("Áudios e cenas excluídos!")
                st.rerun()
            else:
                st.info("Nenhum áudio para excluir.")
                
        if st.button("🖼️ Excluir Imagem Principal", use_container_width=True):
            if delete_game_assets(game_name, "image"):
                st.success("Imagem principal excluída!")
                st.rerun()
            else:
                st.info("Nenhuma imagem para excluir.")
                
        if st.button("🎬 Excluir Vídeo Final", use_container_width=True):
            if delete_game_assets(game_name, "video"):
                st.success("Vídeo final excluído!")
                st.rerun()
            else:
                st.info("Nenhum vídeo para excluir.")
                
        if st.button("📝 Excluir Roteiro (JSON)", use_container_width=True):
            dest_dir = save_assets_dir(game_name)
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
        if st.button("🚨 Excluir Todo o Jogo", use_container_width=True, type="primary"):
            if delete_game_assets(game_name, "all"):
                st.success(f"Jogo '{game_name}' removido por completo!")
                st.session_state.game_name_val = ""
                st.session_state.loaded_game_name = None
                st.session_state.script = None
                st.session_state.bgg_images = None
                st.rerun()
            else:
                st.error("Erro ao deletar diretório.")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("Desenvolvido por Gemini CLI 🤖")
