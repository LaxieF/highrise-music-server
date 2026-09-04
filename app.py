import os
from flask import Flask, request, jsonify
import requests
import yt_dlp

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "service": "Highrise Music Streamer API",
        "message": "Servidor activo y listo."
    }), 200

@app.route("/play", methods=["POST"])
def play_song():
    data = request.get_json() or {}
    query = data.get("query")

    if not query:
        return jsonify({"error": "Falta la búsqueda"}), 400

    video_id = None
    title = query
    duration = 180

    # 1. Buscar el video mediante API pública alternativa (Piped)
    try:
        piped_resp = requests.get(
            f"https://pipedapi.kavin.rocks/search?q={requests.utils.quote(query)}&filter=music_videos",
            timeout=8
        )
        if piped_resp.status_code == 200:
            results = piped_resp.json().get("items", [])
            if results:
                first = results[0]
                # Extraer ID del video
                url_path = first.get("url", "")
                if "/watch?v=" in url_path:
                    video_id = url_path.split("/watch?v=")[1]
                title = first.get("title", query)
                duration = first.get("duration", 180)
    except Exception as e:
        print(f"Error al buscar en API alternativa: {e}")

    # Si no se obtuvo un ID por Piped, intentamos con SoundCloud vía yt-dlp
    target_url = f"https://www.youtube.com/watch?v={video_id}" if video_id else f"scsearch1:{query}"

    # 2. Extraer el enlace directo de audio
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(target_url, download=False)
            if 'entries' in info and len(info['entries']) > 0:
                info = info['entries'][0]

            audio_url = info.get('url')
            if not title or title == query:
                title = info.get('title', query)
            if not duration:
                duration = info.get('duration', 180)

            if not audio_url:
                return jsonify({"error": "No se pudo extraer el audio"}), 404

            return jsonify({
                "status": "success",
                "title": title,
                "stream_url": audio_url,
                "duration": duration
            }), 200

    except Exception as e:
        return jsonify({"error": f"Error al procesar audio: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
