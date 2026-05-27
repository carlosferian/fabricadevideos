import pdfplumber
import requests
import json
import os
import time
import xmltodict
import edge_tts
import asyncio
from dotenv import load_dotenv
from PIL import Image, ImageFilter, ImageDraw, ImageFont
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, VideoClip, concatenate_audioclips

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if OPENROUTER_API_KEY:
    masked_key = OPENROUTER_API_KEY[:6] + "..." + OPENROUTER_API_KEY[-4:]
    print(f"DEBUG: Chave API carregada: {masked_key}")
else:
    print("DEBUG: Chave API NÃO encontrada no .env")

def extract_text_from_pdf(pdf_path):
    """Extrai todo o texto de um arquivo PDF."""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                content = page.extract_text()
                if content:
                    text += content + "\n"
    except Exception as e:
        print(f"Erro ao ler PDF: {e}")
    return text

def generate_script(game_name, manual_text, video_level):
    """Gera um roteiro de vídeo usando o OpenRouter."""
    if not OPENROUTER_API_KEY:
        return "Erro: OPENROUTER_API_KEY não configurada no arquivo .env"

    prompt = f"""
    Você é um roteirista especializado em boardgames e vídeos curtos (TikTok/Reels/Shorts).
    Objetivo: Criar um roteiro para um vídeo de 60 segundos sobre o jogo "{game_name}".
    Nível do público: {video_level}
    
    Contexto (Manual do Jogo):
    {manual_text}
    
    Instruções:
    1. O roteiro deve ser dividido em cenas (máximo 6 cenas).
    2. Cada cena deve ter as seguintes chaves JSON exatas:
       - 'scene': o número da cena (1, 2, 3...)
       - 'narration': O texto falado na narração (em português, tom altamente empolgante e explicativo).
       - 'visual': Descrição do componente real do jogo que deve aparecer nessa cena.
       - 'animation': O tipo de movimento de câmera ideal baseado semanticamente na narração da cena. Escolha estritamente entre uma dessas 4 opções de string:
         * "Zoom Dinâmico (Zoom In)": Use para focar em componentes específicos, dar zoom em detalhes do tabuleiro, ou apresentar componentes novos citados na narração.
         * "Afastamento Suave (Zoom Out)": Use para introduções de jogo (revelando a caixa inteira), conclusões ou planos de visão geral de setup do tabuleiro.
         * "Panorâmica Lateral (Pan)": Use para varrer uma mesa de componentes, fileiras de cartas dispostas, ou progressão de regras.
         * "Estática": Use quando não houver necessidade de movimento de câmera.
    
    Exemplo de formato esperado:
    {{
      "scenes": [
        {{
          "scene": 1,
          "visual": "Caixa do jogo Catan sendo revelada na mesa",
          "narration": "Você está pronto para colonizar a ilha mais famosa dos tabuleiros?",
          "animation": "Afastamento Suave (Zoom Out)"
        }}
      ]
    }}
    
    Retorne APENAS o JSON válido estruturado de acordo com o exemplo acima.
    """

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "HTTP-Referer": "https://github.com/gemini-cli/fabricadevideos",
                    "X-OpenRouter-Title": "Fabrica de Videos",
                },
                data=json.dumps({
                    "model": "openrouter/auto",
                    "messages": [
                        {"role": "system", "content": "Você é um assistente especializado em criar roteiros de vídeos de jogos. Responda APENAS com o JSON."},
                        {"role": "user", "content": prompt}
                    ]
                })
            )
            
            if response.status_code == 429:
                time.sleep(2 ** attempt + 1)
                continue

            result = response.json()
            if "choices" in result:
                script_content = result["choices"][0]["message"]["content"]
                script_content = script_content.replace("```json", "").replace("```", "").strip()
                return json.loads(script_content)
            else:
                return f"Erro na API: {result.get('error', {}).get('message', 'Erro desconhecido')}"
        except Exception as e:
            if attempt == max_retries - 1:
                return f"Erro ao gerar roteiro: {str(e)}"
            time.sleep(1)

def get_bgg_game_images(bgg_id_or_url):
    """
    Obtém a imagem do jogo via API XML v2 do BGG (não requer autenticação).
    Aceita ID numérico ou URL completa do BGG.
    """
    import re

    # Extrai o ID numérico da entrada
    clean_id = re.sub(r'\D', '', str(bgg_id_or_url))
    if not clean_id:
        print("BGG: ID numérico não encontrado na entrada.")
        return None

    api_url = f"https://www.boardgamegeek.com/xmlapi2/thing?id={clean_id}&type=boardgame"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/xml,text/xml,*/*',
    }

    try:
        response = requests.get(api_url, headers=headers, timeout=20)
        print(f"BGG API status: {response.status_code}")

        if response.status_code == 200:
            data = xmltodict.parse(response.text)
            item = data.get("items", {}).get("item")
            if not item:
                print("BGG API: nenhum jogo encontrado para esse ID.")
                return None

            # xmltodict retorna dict quando há 1 item, lista quando há vários
            if isinstance(item, list):
                item = item[0]

            image_url = item.get("image", "").strip()
            thumb_url = item.get("thumbnail", image_url).strip()

            # A API retorna URLs sem protocolo em alguns casos
            if image_url.startswith("//"):
                image_url = "https:" + image_url
            if thumb_url.startswith("//"):
                thumb_url = "https:" + thumb_url

            if image_url:
                return {"main_image": image_url, "thumbnail": thumb_url}

            print("BGG API: URL de imagem não encontrada na resposta.")
            return None

        print(f"BGG API falhou: Status {response.status_code}")
        return None
    except Exception as e:
        print(f"Erro ao buscar imagem via BGG API: {e}")
        return None

def save_assets_dir(game_name):
    """Cria o diretório de assets para o jogo."""
    path = os.path.join("assets", game_name.lower().replace(" ", "_"))
    os.makedirs(path, exist_ok=True)
    return path

def download_image(url, game_name, filename):
    """Faz o download de uma imagem para a pasta de assets."""
    if not url:
        return None
    try:
        dest_dir = save_assets_dir(game_name)
        path = os.path.join(dest_dir, filename)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://boardgamegeek.com/',
            'Accept': 'image/avif,image/webp,image/apng,image/*,*/*;q=0.8',
        }
        response = requests.get(url, stream=True, headers=headers, timeout=30, allow_redirects=True)
        if response.status_code == 200:
            with open(path, 'wb') as f:
                for chunk in response.iter_content(8192):
                    f.write(chunk)
            print(f"Imagem salva em: {path}")
            return path
        print(f"Download falhou: Status {response.status_code} para {url}")
    except Exception as e:
        print(f"Erro download: {e}")
    return None

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

def generate_audio_elevenlabs(text, output_path, voice_id="9bwts2yqj2tUf5FB21IV", api_key=None):
    """
    Gera áudio a partir do texto usando a API do ElevenLabs (síncrono/HTTP).
    A voz padrão é a Letícia (9bwts2yqj2tUf5FB21IV).
    """
    key = api_key or ELEVENLABS_API_KEY
    if not key:
        print("ElevenLabs: API Key não configurada. Fallback para erro.")
        return None
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": key,
        "Content-Type": "application/json",
        "accept": "audio/mpeg"
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"ElevenLabs: Áudio salvo em {output_path}")
            return output_path
        else:
            print(f"ElevenLabs: Erro {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"ElevenLabs: Erro na requisição: {e}")
        return None

async def generate_audio_elevenlabs_async(text, output_path, voice_id="9bwts2yqj2tUf5FB21IV", api_key=None):
    """Gera áudio usando ElevenLabs assincronamente (roda via thread pool para manter concorrência)."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, generate_audio_elevenlabs, text, output_path, voice_id, api_key)

async def generate_audio(text, output_path, voice="pt-BR-FranciscaNeural"):
    """Gera um arquivo de áudio a partir de texto usando edge-tts."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)
    return output_path

def run_generate_audio(text, output_path, voice="pt-BR-FranciscaNeural"):
    """Wrapper síncrono para a função assíncrona de áudio."""
    try:
        asyncio.run(generate_audio(text, output_path, voice))
        return output_path
    except Exception as e:
        print(f"Erro ao gerar áudio: {e}")
        return None

async def generate_multiple_audios(tasks_list):
    """
    Gera múltiplos áudios em paralelo usando edge-tts ou ElevenLabs.
    tasks_list deve ser uma lista de dicionários ou tuplas contendo os parâmetros de geração.
    """
    async_tasks = []
    for item in tasks_list:
        if isinstance(item, dict):
            text = item.get("text")
            path = item.get("path")
            engine = item.get("engine", "edge-tts")
            voice = item.get("voice", "pt-BR-FranciscaNeural")
            voice_id = item.get("voice_id", "9bwts2yqj2tUf5FB21IV")
            api_key = item.get("api_key")
        else:
            text, path, voice = item
            engine = "edge-tts"
            voice_id = "9bwts2yqj2tUf5FB21IV"
            api_key = None
            
        if engine == "elevenlabs":
            async_tasks.append(generate_audio_elevenlabs_async(text, path, voice_id, api_key))
        else:
            communicate = edge_tts.Communicate(text, voice)
            async_tasks.append(communicate.save(path))
            
    await asyncio.gather(*async_tasks)
    return True

def run_generate_multiple_audios(tasks_list):
    """
    Wrapper síncrono e thread-safe para gerar múltiplos áudios em paralelo,
    evitando conflitos com loops de eventos ativos no Streamlit.
    """
    try:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, generate_multiple_audios(tasks_list))
            return future.result()
    except Exception as e:
        print(f"Erro ao gerar áudios em lote paralelo: {e}")
        return False

def search_game_images_ddg(query, max_results=5):
    """
    Busca imagens na web (via Bing Image Search) de forma extremamente robusta e inteligente,
    utilizando normalização de acentos, múltiplas variações de consulta sob o capô,
    filtro rigoroso contra bancos comerciais e pontuação de relevância heurística.
    """
    import urllib.parse
    import requests
    import re
    import html
    import unicodedata

    # Termos positivos para impulsionar a pontuação de board games
    BOARD_GAME_TERMS = [
        "jogo", "tabuleiro", "boardgame", "board game", "estrela", "monopoly", 
        "brinquedo", "caixa", "peças", "cartas", "manual", "gameplay", "peça", 
        "dados", "play", "divertido", "infantil"
    ]

    # Termos bancários e logotipos comerciais para penalizar fortemente ou bloquear
    BANKING_TERMS = [
        "banesco", "bancodevenezuela", "bolivariano", "bancolombia", "pichincha", 
        "guayaquil", "bancaribe", "banplus", "bancamiga", "mercantil", "provincial",
        "banco de venezuela", "banco de ecuador", "banco central", "ahorro", "crédito",
        "credito", "finanças", "finanzas", "dinero", "money", "currency", "dolar",
        "dólar", "economista", "logos de bancos", "bank logo", "banca", "cooperativa",
        "banco de españa", "banco de bogota", "banco de occidente", "banco popular"
    ]

    def normalize_text(text):
        """Normaliza o texto: remove acentos e converte para minúsculas."""
        if not text:
            return ""
        normalized = "".join(
            c for c in unicodedata.normalize('NFD', text)
            if unicodedata.category(c) != 'Mn'
        )
        return normalized.lower().strip()

    def score_result(title, url, original_query):
        """Calcula uma pontuação de relevância baseada em heurísticas para o resultado."""
        norm_title = normalize_text(title)
        norm_url = normalize_text(url)
        norm_query = normalize_text(original_query)
        
        score = 0
        
        # 1. Palavras principais da busca: se o título contém palavras chaves da busca core
        core_query_words = [w for w in norm_query.split() if w not in ["board", "game", "boardgame", "jogo", "de", "tabuleiro"]]
        for w in core_query_words:
            if len(w) > 2 and w in norm_title:
                score += 15
                
        # 2. Impulsionamento por termos de board game
        for term in BOARD_GAME_TERMS:
            if term in norm_title or term in norm_url:
                score += 10
                
        # 3. Penalização severa de bancos comerciais e logotipos genéricos
        for term in BANKING_TERMS:
            if term in norm_title or term in norm_url:
                score -= 100
                
        # 4. Impulsionamento por lojas de brinquedos ou e-commerce conhecidos
        for shop in ["magazineluiza", "mlcdn", "mercadolivre", "estrela.com.br", "amazon", "shopee", "casasbahia", "pontofrio"]:
            if shop in norm_url:
                score += 20
                
        return score

    def search_bing_single(q):
        clean_q = normalize_text(q)
        encoded_query = urllib.parse.quote_plus(clean_q)
        url = f"https://www.bing.com/images/search?q={encoded_query}&form=HDRSC2&first=1"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://www.bing.com/"
        }
        
        results = []
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                tags = re.findall(r'<a[^>]+class="iusc"[^>]+>', response.text)
                for tag in tags:
                    m_match = re.search(r'm="([^"]+)"', tag)
                    if m_match:
                        m_clean = html.unescape(m_match.group(1))
                        murl_match = re.search(r'"murl":"([^"]+)"', m_clean)
                        turl_match = re.search(r'"turl":"([^"]+)"', m_clean)
                        label_match = re.search(r'aria-label="([^"]+)"', tag)
                        
                        title = "Imagem do Jogo"
                        if label_match:
                            title = label_match.group(1).replace("Resultado de imagem para ", "").replace("Image result for ", "")
                            
                        if murl_match:
                            img_url = murl_match.group(1)
                            thumb_url = turl_match.group(1) if turl_match else img_url
                            results.append({
                                "title": title,
                                "main_image": img_url,
                                "thumbnail": thumb_url
                            })
        except Exception as e:
            print(f"Erro ao buscar no Bing para '{q}': {e}")
        return results

    print(f"Buscando imagens para: '{query}' via motor de busca inteligente...")
    
    # 1. Gerar variações da busca
    variations = [query]
    
    # Remover sufixos em inglês/gerais para ver se melhora buscas locais em português
    clean_q = query
    for suffix in ["board game", "boardgame", "jogo de tabuleiro", "jogo"]:
        clean_q = re.sub(rf"\b{suffix}\b", "", clean_q, flags=re.IGNORECASE).strip()
    
    if clean_q and clean_q.lower() != query.lower():
        variations.append(clean_q)
        
    # Tratamento especial para o Banco Imobiliário (Monopoly Brasil)
    norm_query = normalize_text(query)
    if "banco imobiliario" in norm_query:
        variations.append("banco imobiliario")
        variations.append("Monopoly Brasil")
        
    # 2. Executar as buscas de todas as variações e pontuar
    all_raw_results = []
    seen_urls = set()
    
    for var in variations:
        res = search_bing_single(var)
        for item in res:
            url = item["main_image"]
            if url not in seen_urls:
                seen_urls.add(url)
                score = score_result(item["title"], url, query)
                item["score"] = score
                all_raw_results.append(item)
                
    # 3. Ordenar resultados por relevância (pontuação descendente) e remover penalizados (<0)
    all_raw_results.sort(key=lambda x: x["score"], reverse=True)
    filtered_results = [item for item in all_raw_results if item["score"] >= 0]
    
    print(f"Busca inteligente concluída. Resultados brutos: {len(all_raw_results)}, Filtrados e validados: {len(filtered_results)}")
    
    return filtered_results[:max_results]

def wrap_text(text, font, max_width, draw):
    """Quebra o texto em várias linhas para caber na largura máxima."""
    words = text.split(" ")
    lines = []
    current_line = []
    
    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        width = bbox[2] - bbox[0]
        if width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                lines.append(word)
                current_line = []
                
    if current_line:
        lines.append(" ".join(current_line))
    return lines

def ensure_default_bg_music():
    """Garante que existam trilhas sonoras padrões na pasta assets/bg_music/."""
    bg_music_dir = os.path.join("assets", "bg_music")
    os.makedirs(bg_music_dir, exist_ok=True)
    
    tracks = {
        "synth_pulse.mp3": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
        "retro_groove.mp3": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
        "chill_wave.mp3": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3"
    }
    
    downloaded = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    for filename, url in tracks.items():
        path = os.path.join(bg_music_dir, filename)
        if not os.path.exists(path):
            try:
                print(f"BGM: Baixando {filename} de {url}...")
                response = requests.get(url, headers=headers, timeout=30)
                if response.status_code == 200:
                    with open(path, "wb") as f:
                        f.write(response.content)
                    print(f"BGM: {filename} salvo com sucesso.")
                    downloaded.append(filename)
                else:
                    print(f"BGM: Falha ao baixar {filename} (Status {response.status_code})")
            except Exception as e:
                print(f"BGM: Erro ao baixar {filename}: {e}")
    return downloaded

def get_dominant_colors(image, num_colors=2):
    """Retorna as duas cores predominantes da imagem."""
    try:
        img_temp = image.copy()
        img_temp.thumbnail((100, 100))
        quantized = img_temp.quantize(colors=num_colors)
        palette = quantized.getpalette()
        if palette is not None and len(palette) >= 6:
            c1 = (palette[0], palette[1], palette[2])
            c2 = (palette[3], palette[4], palette[5])
            return c1, c2
        elif palette is not None and len(palette) >= 3:
            c1 = (palette[0], palette[1], palette[2])
            return c1, c1
        else:
            return (30, 30, 45), (15, 15, 20)
    except Exception as e:
        print(f"Erro ao obter cores predominantes: {e}")
        return (30, 30, 45), (15, 15, 20)

def create_linear_gradient(color1, color2, width=1080, height=1920):
    """Cria uma imagem de gradiente linear de cima para baixo."""
    base = Image.new("RGB", (width, height), color1)
    top = Image.new("RGB", (width, height), color2)
    mask = Image.new("L", (width, height))
    mask_data = []
    for y in range(height):
        factor = int((y / height) * 255)
        mask_data.extend([factor] * width)
    mask.putdata(mask_data)
    return Image.composite(top, base, mask)

def round_corners(image, radius=30):
    """Adiciona cantos arredondados a uma imagem Pillow."""
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([0, 0, image.size[0], image.size[1]], radius=radius, fill=255)
    result = Image.new("RGBA", image.size)
    result.paste(image, (0, 0), mask=mask)
    return result

def create_scene_frame(image_path, text, scene_num, game_name, width=1080, height=1920, visual_style="Clássico"):
    """
    Cria um frame de vídeo vertical (9:16) com o estilo visual configurado,
    imagem original centralizada e legenda formatada.
    Retorna o caminho temporário da imagem salva.
    """
    try:
        im = Image.open(image_path)
        im_w, im_h = im.size
    except Exception as e:
        print(f"Erro ao abrir imagem {image_path}: {e}")
        im = Image.new("RGB", (800, 600), color="gray")
        im_w, im_h = im.size

    # --- 1. CONFIGURAÇÃO DE BACKGROUND SEGUNDO O ESTILO ---
    bg_ratio = width / height
    im_ratio = im_w / im_h
    
    # Gerar a imagem base escalada
    if im_ratio > bg_ratio:
        # Imagem horizontal
        new_h = height
        new_w = int(im_w * (height / im_h))
        im_scaled = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
        left = (new_w - width) // 2
        bg = im_scaled.crop((left, 0, left + width, height))
    else:
        # Imagem vertical
        new_w = width
        new_h = int(im_h * (width / im_w))
        im_scaled = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
        top = (new_h - height) // 2
        bg = im_scaled.crop((0, top, width, top + height))

    # Aplicar o estilo visual selecionado
    if visual_style == "Gradiente Moderno":
        # Extrair cores dominantes e criar um gradiente de fundo
        color1, color2 = get_dominant_colors(im, num_colors=2)
        # Atenuar as cores do gradiente para não ficarem gritantes
        color1 = tuple(int(x * 0.6) for x in color1)
        color2 = tuple(int(x * 0.3) for x in color2)
        bg = create_linear_gradient(color1, color2, width, height)
    elif visual_style == "Neon Dark":
        # Fundo desfocado extra escuro (Dark Cyberpunk)
        bg = bg.filter(ImageFilter.GaussianBlur(radius=50))
        darken = Image.new("RGBA", (width, height), (0, 0, 0, 160)) # 62% escurecimento
        bg = Image.composite(darken, bg.convert("RGBA"), darken.split()[3]).convert("RGB")
    else: # "Clássico"
        bg = bg.filter(ImageFilter.GaussianBlur(radius=30))

    # --- 2. CENTRALIZAR IMAGEM PRINCIPAL ---
    max_w = width - 120  # 960px de largura máxima
    scale_factor = max_w / im_w
    center_w = max_w
    center_h = int(im_h * scale_factor)
    
    max_h = int(height * 0.55)
    if center_h > max_h:
        scale_factor = max_h / im_h
        center_h = max_h
        center_w = int(im_w * scale_factor)
        
    center_x = (width - center_w) // 2
    center_y = (height - center_h) // 2 - 50
    
    center_im = im.resize((center_w, center_h), Image.Resampling.LANCZOS)
    
    if visual_style == "Gradiente Moderno":
        # Desenhar uma borda branca arredondada
        border_pad = 6
        draw_bg = ImageDraw.Draw(bg)
        draw_bg.rounded_rectangle(
            [center_x - border_pad, center_y - border_pad, center_x + center_w + border_pad, center_y + center_h + border_pad],
            radius=35 + border_pad,
            fill="white"
        )
        # Centralizar imagem com cantos arredondados
        rounded_im = round_corners(center_im, radius=35)
        bg.paste(rounded_im, (center_x, center_y), mask=rounded_im)
        
    elif visual_style == "Neon Dark":
        # Selecionar cor neon baseada no número da cena
        neon_colors = ["#ff007f", "#00f0ff", "#39ff14", "#ffb300"]
        neon_color = neon_colors[scene_num % len(neon_colors)]
        
        # Desenhar borda neon
        border_pad = 6
        draw_bg = ImageDraw.Draw(bg)
        draw_bg.rounded_rectangle(
            [center_x - border_pad, center_y - border_pad, center_x + center_w + border_pad, center_y + center_h + border_pad],
            radius=30 + border_pad,
            fill=neon_color
        )
        # Borda interna preta de isolamento
        draw_bg.rounded_rectangle(
            [center_x - 2, center_y - 2, center_x + center_w + 2, center_y + center_h + 2],
            radius=30 + 2,
            fill="black"
        )
        # Colar a imagem com cantos arredondados
        rounded_im = round_corners(center_im, radius=30)
        bg.paste(rounded_im, (center_x, center_y), mask=rounded_im)
        
    else: # "Clássico"
        border_width = 4
        bordered_im = Image.new("RGB", (center_w + 2*border_width, center_h + 2*border_width), color="white")
        bordered_im.paste(center_im, (border_width, border_width))
        bg.paste(bordered_im, (center_x - border_width, center_y - border_width))

    # --- 3. LEGENDAS ---
    draw = ImageDraw.Draw(bg)
    
    font = None
    for font_name in ["arial.ttf", "calibri.ttf", "segoeui.ttf"]:
        try:
            font = ImageFont.truetype(font_name, 38)
            break
        except Exception:
            continue
            
    if font is None:
        font = ImageFont.load_default()
        
    box_w = width - 120
    box_padding = 30
    text_max_w = box_w - (2 * box_padding)
    
    lines = wrap_text(text, font, text_max_w, draw)
    
    if lines:
        line_bbox = draw.textbbox((0, 0), lines[0], font=font)
        line_height = line_bbox[3] - line_bbox[1]
    else:
        line_height = 40
        
    line_spacing = 12
    box_h = (len(lines) * line_height) + ((len(lines) - 1) * line_spacing) + (2 * box_padding)
    box_x = 60
    box_y = height - box_h - 150
    
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    if visual_style == "Neon Dark":
        neon_colors = ["#ff007f", "#00f0ff", "#39ff14", "#ffb300"]
        neon_color = neon_colors[scene_num % len(neon_colors)]
        
        # Caixa de legenda translúcida escura com outline neon brilhante
        overlay_draw.rounded_rectangle(
            [box_x, box_y, box_x + box_w, box_y + box_h],
            radius=15,
            fill=(10, 10, 15, 210), # Preto translúcido denso
            outline=neon_color,
            width=3
        )
    elif visual_style == "Gradiente Moderno":
        # Caixa cinza escura suave e translúcida
        overlay_draw.rounded_rectangle(
            [box_x, box_y, box_x + box_w, box_y + box_h],
            radius=15,
            fill=(15, 15, 22, 190)
        )
    else: # "Clássico"
        overlay_draw.rounded_rectangle(
            [box_x, box_y, box_x + box_w, box_y + box_h],
            radius=15,
            fill=(0, 0, 0, 180)
        )
    
    bg = Image.alpha_composite(bg.convert("RGBA"), overlay)
    draw_final = ImageDraw.Draw(bg)
    
    current_y = box_y + box_padding
    for line in lines:
        line_bbox = draw_final.textbbox((0, 0), line, font=font)
        line_w = line_bbox[2] - line_bbox[0]
        line_x = box_x + (box_w - line_w) // 2
        draw_final.text((line_x, current_y), line, font=font, fill="white")
        current_y += line_height + line_spacing
        
    dest_dir = save_assets_dir(game_name)
    temp_frame_path = os.path.join(dest_dir, f"temp_frame_{scene_num}.jpg")
    bg.convert("RGB").save(temp_frame_path, "JPEG")
    return temp_frame_path

def create_animated_scene_clip(image_path, text, scene_num, game_name, duration, width=1080, height=1920, visual_style="Clássico", animation_type="Zoom Dinâmico (Zoom In)"):
    """
    Gera um VideoClip da MoviePy para a cena, aplicando efeitos de animação local
    como Ken Burns (Zoom In, Zoom Out, Pan) processados em tempo real na memória.
    """
    import numpy as np
    from PIL import Image, ImageFilter, ImageDraw, ImageFont
    from moviepy import VideoClip

    try:
        im = Image.open(image_path)
        im_w, im_h = im.size
    except Exception as e:
        print(f"Erro ao abrir imagem {image_path}: {e}")
        im = Image.new("RGB", (800, 600), color="gray")
        im_w, im_h = im.size

    # --- 1. CONFIGURAÇÃO DE BACKGROUND E BASE ---
    bg_ratio = width / height
    im_ratio = im_w / im_h
    
    if im_ratio > bg_ratio:
        new_h = height
        new_w = int(im_w * (height / im_h))
        im_scaled = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
        left = (new_w - width) // 2
        bg = im_scaled.crop((left, 0, left + width, height))
    else:
        new_w = width
        new_h = int(im_h * (width / im_w))
        im_scaled = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
        top = (new_h - height) // 2
        bg = im_scaled.crop((0, top, width, top + height))

    # Aplicar o estilo visual ao background
    if visual_style == "Gradiente Moderno":
        color1, color2 = get_dominant_colors(im, num_colors=2)
        color1 = tuple(int(x * 0.6) for x in color1)
        color2 = tuple(int(x * 0.3) for x in color2)
        bg_static = create_linear_gradient(color1, color2, width, height)
    elif visual_style == "Neon Dark":
        bg_static = bg.filter(ImageFilter.GaussianBlur(radius=50))
        darken = Image.new("RGBA", (width, height), (0, 0, 0, 160))
        bg_static = Image.composite(darken, bg_static.convert("RGBA"), darken.split()[3]).convert("RGB")
    else: # "Clássico"
        bg_static = bg.filter(ImageFilter.GaussianBlur(radius=30))

    # --- 2. PREPARAR TEXTO/LEGENDA E TEXTO OVERLAY ---
    overlay_static = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay_static)
    
    font = None
    for font_name in ["arial.ttf", "calibri.ttf", "segoeui.ttf"]:
        try:
            font = ImageFont.truetype(font_name, 38)
            break
        except Exception:
            continue
    if font is None:
        font = ImageFont.load_default()

    box_w = width - 120
    box_padding = 30
    text_max_w = box_w - (2 * box_padding)
    lines = wrap_text(text, font, text_max_w, draw_overlay)
    
    if lines:
        line_bbox = draw_overlay.textbbox((0, 0), lines[0], font=font)
        line_height = line_bbox[3] - line_bbox[1]
    else:
        line_height = 40
        
    line_spacing = 12
    box_h = (len(lines) * line_height) + ((len(lines) - 1) * line_spacing) + (2 * box_padding)
    box_x = 60
    box_y = height - box_h - 150
    
    if visual_style == "Neon Dark":
        neon_colors = ["#ff007f", "#00f0ff", "#39ff14", "#ffb300"]
        neon_color = neon_colors[scene_num % len(neon_colors)]
        draw_overlay.rounded_rectangle(
            [box_x, box_y, box_x + box_w, box_y + box_h],
            radius=15,
            fill=(10, 10, 15, 210),
            outline=neon_color,
            width=3
        )
    elif visual_style == "Gradiente Moderno":
        draw_overlay.rounded_rectangle(
            [box_x, box_y, box_x + box_w, box_y + box_h],
            radius=15,
            fill=(15, 15, 22, 190)
        )
    else: # "Clássico"
        draw_overlay.rounded_rectangle(
            [box_x, box_y, box_x + box_w, box_y + box_h],
            radius=15,
            fill=(0, 0, 0, 180)
        )
        
    current_y = box_y + box_padding
    for line in lines:
        line_bbox = draw_overlay.textbbox((0, 0), line, font=font)
        line_w = line_bbox[2] - line_bbox[0]
        line_x = box_x + (box_w - line_w) // 2
        draw_overlay.text((line_x, current_y), line, font=font, fill="white")
        current_y += line_height + line_spacing

    # --- 3. CONFIGURAR A IMAGEM CENTRAL BASE ---
    max_w = width - 120
    scale_factor = max_w / im_w
    center_w = max_w
    center_h = int(im_h * scale_factor)
    
    max_h = int(height * 0.55)
    if center_h > max_h:
        scale_factor = max_h / im_h
        center_h = max_h
        center_w = int(im_w * scale_factor)
        
    center_im = im.resize((center_w, center_h), Image.Resampling.LANCZOS)
    center_x = (width - center_w) // 2
    center_y = (height - center_h) // 2 - 50

    def get_frame(t):
        frame_img = bg_static.copy()
        progress = min(t / duration, 1.0)
        
        zoom = 1.0
        offset_x = 0
        offset_y = 0
        
        if animation_type == "Zoom Dinâmico (Zoom In)":
            zoom = 1.0 + 0.12 * progress
        elif animation_type == "Afastamento Suave (Zoom Out)":
            zoom = 1.12 - 0.12 * progress
        elif animation_type == "Panorâmica Lateral (Pan)":
            zoom = 1.10
            max_pan = int(center_w * 0.05)
            offset_x = int(-max_pan + (2 * max_pan * progress))

        w_anim = int(center_w * zoom)
        h_anim = int(center_h * zoom)
        
        w_anim = max(10, min(w_anim, width * 2))
        h_anim = max(10, min(h_anim, height * 2))
        
        center_im_anim = center_im.resize((w_anim, h_anim), Image.Resampling.LANCZOS)
        
        x_anim = center_x + (center_w - w_anim) // 2 + offset_x
        y_anim = center_y + (center_h - h_anim) // 2 + offset_y
        
        center_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw_center = ImageDraw.Draw(center_layer)
        
        if visual_style == "Gradiente Moderno":
            border_pad = 6
            draw_center.rounded_rectangle(
                [x_anim - border_pad, y_anim - border_pad, x_anim + w_anim + border_pad, y_anim + h_anim + border_pad],
                radius=35 + border_pad,
                fill="white"
            )
            rounded_im = round_corners(center_im_anim, radius=35)
            center_layer.paste(rounded_im, (x_anim, y_anim), mask=rounded_im)
            
        elif visual_style == "Neon Dark":
            neon_colors = ["#ff007f", "#00f0ff", "#39ff14", "#ffb300"]
            neon_color = neon_colors[scene_num % len(neon_colors)]
            border_pad = 6
            draw_center.rounded_rectangle(
                [x_anim - border_pad, y_anim - border_pad, x_anim + w_anim + border_pad, y_anim + h_anim + border_pad],
                radius=30 + border_pad,
                fill=neon_color
            )
            draw_center.rounded_rectangle(
                [x_anim - 2, y_anim - 2, x_anim + w_anim + 2, y_anim + h_anim + 2],
                radius=30 + 2,
                fill="black"
            )
            rounded_im = round_corners(center_im_anim, radius=30)
            center_layer.paste(rounded_im, (x_anim, y_anim), mask=rounded_im)
            
        else: # "Clássico"
            border_width = 4
            bordered_im = Image.new("RGB", (w_anim + 2*border_width, h_anim + 2*border_width), color="white")
            bordered_im.paste(center_im_anim, (border_width, border_width))
            center_layer.paste(bordered_im, (x_anim - border_width, y_anim - border_width))
            
        final_frame = Image.alpha_composite(frame_img.convert("RGBA"), center_layer)
        final_frame = Image.alpha_composite(final_frame, overlay_static)
        
        return np.array(final_frame.convert("RGB"))

    return VideoClip(get_frame, duration=duration)

def render_video(game_name, script, visual_style="Clássico", bg_music_name="Sem Música", bg_volume=0.15, animation_type="Estática"):
    """
    Renderiza o vídeo final a partir da imagem do jogo e os áudios das cenas.
    Permite mixar música de fundo (BGM), aplicar estilos visuais diferenciados e animações locais.
    Salva em assets/{game_name}/video_final.mp4.
    Retorna o caminho do vídeo gerado ou None se houver erro.
    """
    # Garante que as músicas de fundo padrão estejam disponíveis
    ensure_default_bg_music()
    
    dest_dir = save_assets_dir(game_name)
    image_path = os.path.join(dest_dir, "main_game.jpg")
    
    if not os.path.exists(image_path):
        print(f"Erro: imagem principal {image_path} não encontrada.")
        return None
        
    scene_clips = []
    temp_frames = []
    
    try:
        # 1. Renderiza cada cena/clipe individualmente e carrega as locuções correspondentes
        for scene in script:
            scene_num = scene.get("scene", 0)
            narration = scene.get("narration", "")
            audio_path = os.path.join(dest_dir, f"scene_{scene_num}.mp3")
            
            if not os.path.exists(audio_path):
                print(f"Erro: áudio da cena {scene_num} não encontrado.")
                continue
                
            # Determine specific scene image path
            scene_img_path = os.path.join(dest_dir, f"scene_{scene_num}.jpg")
            if not os.path.exists(scene_img_path):
                scene_img_path = os.path.join(dest_dir, f"scene_{scene_num}.png")
            if not os.path.exists(scene_img_path):
                scene_img_path = os.path.join(dest_dir, f"scene_{scene_num}.jpeg")
                
            # If no scene-specific image is found, fall back to global image_path
            current_image_path = scene_img_path if os.path.exists(scene_img_path) else image_path
            
            # Determine animation type for this scene
            scene_animation = scene.get("animation", "Zoom Dinâmico (Zoom In)")
            current_anim = scene_animation if animation_type == "Contextual (Definido no Roteiro)" else animation_type
            
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            
            if current_anim == "Estática" or current_anim == "":
                # Modo clássico estático - gera frame JPG temporário
                temp_frame = create_scene_frame(current_image_path, narration, scene_num, game_name, visual_style=visual_style)
                temp_frames.append(temp_frame)
                scene_clip = ImageClip(temp_frame).with_duration(duration)
            else:
                # Modo animado (Ken Burns) - processado inteiramente em memória via Pillow/MoviePy
                scene_clip = create_animated_scene_clip(
                    image_path=current_image_path,
                    text=narration,
                    scene_num=scene_num,
                    game_name=game_name,
                    duration=duration,
                    visual_style=visual_style,
                    animation_type=current_anim
                )
                
            scene_clip = scene_clip.with_audio(audio_clip)
            scene_clips.append(scene_clip)
            
        if not scene_clips:
            print("Nenhuma cena válida pôde ser carregada para renderização.")
            return None
            
        # 2. Concatena os clipes de imagem/vídeo com áudio
        final_clip = concatenate_videoclips(scene_clips, method="compose")
        
        # 3. Adiciona a trilha de música de fundo (BGM) se configurada
        bg_music_clip = None
        if bg_music_name != "Sem Música":
            bg_music_dir = os.path.join("assets", "bg_music")
            bg_music_path = None
            
            if bg_music_name == "Aleatória":
                if os.path.exists(bg_music_dir):
                    mp3_files = [f for f in os.listdir(bg_music_dir) if f.endswith(".mp3")]
                    if mp3_files:
                        import random
                        bg_music_path = os.path.join(bg_music_dir, random.choice(mp3_files))
            else:
                bg_music_path = os.path.join(bg_music_dir, bg_music_name)
                
            if bg_music_path and os.path.exists(bg_music_path):
                try:
                    from moviepy import CompositeAudioClip
                    bg_music_clip = AudioFileClip(bg_music_path)
                    
                    # Corta ou repete a música para bater com a duração do vídeo
                    if bg_music_clip.duration < final_clip.duration:
                        n_repeats = int(final_clip.duration / bg_music_clip.duration) + 1
                        bg_music_clip = concatenate_audioclips([bg_music_clip] * n_repeats).subclipped(0, final_clip.duration)
                    else:
                        bg_music_clip = bg_music_clip.subclipped(0, final_clip.duration)
                        
                    # Ajusta o volume da música de fundo
                    bg_music_clip = bg_music_clip.with_volume_scaled(bg_volume)
                    
                    # Mescla a narração (áudio do vídeo) com o BGM
                    original_audio = final_clip.audio
                    combined_audio = CompositeAudioClip([original_audio, bg_music_clip])
                    final_clip = final_clip.with_audio(combined_audio)
                    print(f"BGM: Música '{os.path.basename(bg_music_path)}' mesclada com sucesso (volume: {bg_volume}).")
                except Exception as audio_err:
                    print(f"Erro ao adicionar música de fundo: {audio_err}")
            else:
                print(f"BGM: Arquivo '{bg_music_name}' não encontrado em {bg_music_dir}.")
 
        # 4. Grava o arquivo de vídeo final
        output_video_path = os.path.join(dest_dir, "video_final.mp4")
        
        final_clip.write_videofile(
            output_video_path,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile=os.path.join(dest_dir, "temp_audio.m4a"),
            remove_temp=True
        )
        
        # 5. Fecha e limpa os recursos de clipes
        for clip in scene_clips:
            clip.close()
        if bg_music_clip:
            bg_music_clip.close()
        final_clip.close()
        
        return output_video_path
        
    except Exception as e:
        print(f"Erro ao renderizar vídeo: {e}")
        return None
        
    finally:
        for temp_f in temp_frames:
            try:
                if os.path.exists(temp_f):
                    os.remove(temp_f)
            except Exception as e:
                print(f"Erro ao remover frame temporário {temp_f}: {e}")

def save_script_to_file(game_name, script):
    """Salva o JSON do roteiro na pasta de assets do jogo."""
    if not game_name or not script:
        return False
    try:
        dest_dir = save_assets_dir(game_name)
        script_path = os.path.join(dest_dir, "script.json")
        with open(script_path, "w", encoding="utf-8") as f:
            json.dump(script, f, ensure_ascii=False, indent=4)
        print(f"Roteiro salvo com sucesso em: {script_path}")
        return True
    except Exception as e:
        print(f"Erro ao salvar roteiro em arquivo: {e}")
        return False

def load_script_from_file(game_name):
    """Carrega o roteiro salvo na pasta de assets do jogo."""
    if not game_name:
        return None
    try:
        dest_dir = save_assets_dir(game_name)
        script_path = os.path.join(dest_dir, "script.json")
        if os.path.exists(script_path):
            with open(script_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"Erro ao carregar roteiro do arquivo: {e}")
        return None

def extract_images_from_url(url):
    """Extrai imagens de uma página da web usando expressões regulares."""
    import requests
    import re
    from urllib.parse import urljoin
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # Se for uma imagem direta (pela extensão da URL), retorna ela mesma
    url_clean = url.split("?")[0].lower()
    if url_clean.endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
        return [{
            "title": "Imagem Direta URL",
            "main_image": url,
            "thumbnail": url
        }]
        
    results = []
    try:
        # Tenta verificar se é uma imagem direta pelo Content-Type antes de baixar toda a página
        try:
            head = requests.head(url, headers=headers, timeout=5)
            if head.status_code == 200 and "image/" in head.headers.get("Content-Type", "").lower():
                return [{
                    "title": "Imagem Direta URL",
                    "main_image": url,
                    "thumbnail": url
                }]
        except Exception:
            pass

        response = requests.get(url, headers=headers, timeout=12)
        if response.status_code == 200:
            # Verifica se a resposta em si é uma imagem (caso o HEAD não tenha funcionado)
            if "image/" in response.headers.get("Content-Type", "").lower():
                return [{
                    "title": "Imagem Direta URL",
                    "main_image": url,
                    "thumbnail": url
                }]

            # Encontra tags <img src="..."> usando regex
            img_tags = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', response.text, re.IGNORECASE)
            
            seen_urls = set()
            for src in img_tags:
                abs_url = urljoin(url, src)
                if abs_url not in seen_urls:
                    # Filtra pixels e ícones insignificantes
                    if not any(x in abs_url.lower() for x in ["tracker", "pixel", "analytics", ".svg", "sprite", "logo-"]):
                        if abs_url.lower().startswith("http"):
                            seen_urls.add(abs_url)
                            results.append({
                                "title": "Imagem Extraída da Página",
                                "main_image": abs_url,
                                "thumbnail": abs_url
                            })
                            if len(results) >= 10:  # Limita a 10 imagens
                                break
    except Exception as e:
        print(f"Erro ao extrair imagens de {url}: {e}")
    return results

def delete_game_assets(game_name, delete_type):
    """Exclui de forma granular ou total os arquivos gerados de um jogo."""
    import shutil
    if not game_name:
        return False
    try:
        dest_dir = save_assets_dir(game_name)
        if delete_type == "all":
            # Deleta toda a pasta do jogo
            if os.path.exists(dest_dir):
                shutil.rmtree(dest_dir)
                print(f"Diretório deletado com sucesso: {dest_dir}")
                return True
        elif delete_type == "video":
            # Deleta apenas o vídeo final
            video_path = os.path.join(dest_dir, "video_final.mp4")
            if os.path.exists(video_path):
                os.remove(video_path)
                print("Vídeo excluído com sucesso.")
                return True
        elif delete_type == "image":
            # Deleta apenas a imagem principal do jogo
            img_path = os.path.join(dest_dir, "main_game.jpg")
            if os.path.exists(img_path):
                os.remove(img_path)
                print("Imagem principal excluída com sucesso.")
                return True
        elif delete_type == "audio":
            # Deleta todas as narrações em áudio e frames temporários
            files = os.listdir(dest_dir)
            deleted_count = 0
            for f in files:
                if f.startswith("scene_") and f.endswith(".mp3"):
                    os.remove(os.path.join(dest_dir, f))
                    deleted_count += 1
                elif f.startswith("temp_frame_") and f.endswith(".jpg"):
                    os.remove(os.path.join(dest_dir, f))
                    deleted_count += 1
            print(f"Excluídos {deleted_count} arquivos de áudios/cenas.")
            return True
    except Exception as e:
        print(f"Erro ao deletar ativos de tipo '{delete_type}' para o jogo '{game_name}': {e}")
    return False

def generate_social_metadata(game_name, script):
    """
    Gera títulos, legendas e hashtags com base no roteiro gerado para o jogo.
    Retorna um dicionário com os campos 'titles', 'captions' e 'hashtags', ou None se falhar.
    """
    if not OPENROUTER_API_KEY:
        return {"error": "OPENROUTER_API_KEY não configurada no arquivo .env"}

    # Formata o roteiro para texto legível
    script_text = ""
    for i, scene in enumerate(script):
        s_num = scene.get("scene", i + 1)
        s_nar = scene.get("narration", "")
        s_vis = scene.get("visual", "")
        script_text += f"Cena {s_num}:\n- Visual: {s_vis}\n- Locução: {s_nar}\n\n"

    prompt = f"""
    Você é um Copywriter e Especialista em Redes Sociais altamente estratégico para canais de Board Games.
    Com base no roteiro do vídeo abaixo sobre o jogo "{game_name}", gere ideias altamente engajadoras de metadados sociais para publicação no TikTok, Instagram Reels e YouTube Shorts.

    Roteiro do Vídeo:
    {script_text}

    Instruções:
    1. Gere 3 opções de Títulos extremamente chamativos e curtos (máximo 80 caracteres), com gatilhos de curiosidade ou diversão.
    2. Gere 2 opções de Legendas (Copys) para postagem:
       - Opção 1: Direta e focada em engajamento rápido (ideal para TikTok).
       - Opção 2: Narrativa, com um breve gancho, chamada para ação (CTA) como "Marque o amigo" ou "Comente o que achou", ideal para Reels.
    3. Gere um bloco estratégico com cerca de 10 Hashtags de nicho (ex: #boardgames, #jogosdetabuleiro, #dicasdejogos) e do próprio jogo.
    
    Retorne a resposta APENAS como um objeto JSON válido no formato abaixo, sem formatação markdown ou blocos de código (ex: não inclua ```json):
    {{
        "titles": ["Título 1", "Título 2", "Título 3"],
        "captions": ["Legenda Opção 1", "Legenda Opção 2"],
        "hashtags": "#hashtag1 #hashtag2 #hashtag3"
    }}
    """

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://github.com/gemini-cli/fabricadevideos",
                "X-OpenRouter-Title": "Fabrica de Videos",
            },
            data=json.dumps({
                "model": "openrouter/auto",
                "messages": [
                    {"role": "system", "content": "Você é um redator de mídias sociais especializado em jogos de tabuleiro. Responda APENAS com o JSON."},
                    {"role": "user", "content": prompt}
                ]
            }),
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result:
                content = result["choices"][0]["message"]["content"]
                # Limpeza contra markdown ```json
                content = content.replace("```json", "").replace("```", "").strip()
                data = json.loads(content)
                
                # Grava no arquivo metadata.txt na pasta de assets do jogo
                dest_dir = save_assets_dir(game_name)
                metadata_path = os.path.join(dest_dir, "metadata.txt")
                with open(metadata_path, "w", encoding="utf-8") as f:
                    f.write(f"=== TÍTULOS SUGERIDOS ===\n")
                    for i, t in enumerate(data.get("titles", [])):
                        f.write(f"{i+1}. {t}\n")
                    f.write(f"\n=== LEGENDA 1 (TikTok) ===\n{data.get('captions', [''])[0]}\n")
                    if len(data.get("captions", [])) > 1:
                        f.write(f"\n=== LEGENDA 2 (Instagram/Reels) ===\n{data.get('captions', [''])[1]}\n")
                    f.write(f"\n=== HASHTAGS ===\n{data.get('hashtags', '')}\n")
                
                # Grava também um JSON para reuso
                metadata_json_path = os.path.join(dest_dir, "metadata.json")
                with open(metadata_json_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                    
                return data
            else:
                return {"error": f"Erro na resposta da API OpenRouter: {result.get('error', {}).get('message', 'Sem detalhes')}"}
        else:
            return {"error": f"Erro HTTP {response.status_code} na API OpenRouter"}
    except Exception as e:
        print(f"Erro ao gerar metadados sociais: {e}")
        return {"error": str(e)}
