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
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips

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
    2. Cada cena deve ter: 
       - 'narration': O texto que será falado (em português, tom empolgante).
       - 'visual': Descrição do componente real do jogo que deve aparecer.
    3. Retorne APENAS um JSON válido.
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

def create_scene_frame(image_path, text, scene_num, game_name, width=1080, height=1920):
    """
    Cria um frame de vídeo vertical (9:16) com fundo desfocado, imagem original centralizada
    com borda branca, e a legenda estilizada na parte inferior.
    Retorna o caminho temporário da imagem salva.
    """
    try:
        im = Image.open(image_path)
        im_w, im_h = im.size
    except Exception as e:
        print(f"Erro ao abrir imagem {image_path}: {e}")
        im = Image.new("RGB", (800, 600), color="gray")
        im_w, im_h = im.size

    # 1. Criar fundo 9:16 desfocado
    bg_ratio = width / height
    im_ratio = im_w / im_h
    
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
        
    bg = bg.filter(ImageFilter.GaussianBlur(radius=30))
    
    # 2. Centralizar imagem com borda branca
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
    
    border_width = 4
    bordered_im = Image.new("RGB", (center_w + 2*border_width, center_h + 2*border_width), color="white")
    bordered_im.paste(center_im, (border_width, border_width))
    bg.paste(bordered_im, (center_x - border_width, center_y - border_width))
    
    # 3. Legendas
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

def render_video(game_name, script):
    """
    Renderiza o vídeo final a partir da imagem do jogo e os áudios das cenas.
    Salva em assets/{game_name}/video_final.mp4.
    Retorna o caminho do vídeo gerado ou None se houver erro.
    """
    dest_dir = save_assets_dir(game_name)
    image_path = os.path.join(dest_dir, "main_game.jpg")
    
    if not os.path.exists(image_path):
        print(f"Erro: imagem principal {image_path} não encontrada.")
        return None
        
    scene_clips = []
    temp_frames = []
    
    try:
        for scene in script:
            scene_num = scene.get("scene", 0)
            narration = scene.get("narration", "")
            audio_path = os.path.join(dest_dir, f"scene_{scene_num}.mp3")
            
            if not os.path.exists(audio_path):
                print(f"Erro: áudio da cena {scene_num} não encontrado.")
                continue
                
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            
            temp_frame = create_scene_frame(image_path, narration, scene_num, game_name)
            temp_frames.append(temp_frame)
            
            image_clip = ImageClip(temp_frame).with_duration(duration).with_audio(audio_clip)
            scene_clips.append(image_clip)
            
        if not scene_clips:
            print("Nenhuma cena válida pôde ser carregada para renderização.")
            return None
            
        final_clip = concatenate_videoclips(scene_clips, method="compose")
        output_video_path = os.path.join(dest_dir, "video_final.mp4")
        
        final_clip.write_videofile(
            output_video_path,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile=os.path.join(dest_dir, "temp_audio.m4a"),
            remove_temp=True
        )
        
        for clip in scene_clips:
            clip.close()
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
