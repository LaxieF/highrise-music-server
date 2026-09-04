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

    # Configuración optimizada para streams directos de audio no protegidos
    ydl_opts = {
        'format': 'bestaudio[ext=mp3]/bestaudio[ext=m4a]/bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'scsearch1:',
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if info and 'entries' in info and len(info['entries']) > 0:
                info = info['entries'][0]

            if not info or not info.get('url'):
                return jsonify({"error": "No se encontró un audio compatible o sin DRM"}), 404

            audio_url = info.get('url')
            title = info.get('title', query)
            duration = info.get('duration', 180)

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
        
