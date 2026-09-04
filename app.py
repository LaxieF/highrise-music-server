import os
from flask import Flask, request, jsonify, redirect
import yt_dlp

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "online", "service": "Highrise Music API"}), 200

@app.route("/play", methods=["POST"])
def play_song():
    data = request.get_json() or {}
    query = data.get("query")

    if not query:
        return jsonify({"error": "Falta la búsqueda"}), 400

    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch1:',
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if info and 'entries' in info and len(info['entries']) > 0:
                info = info['entries'][0]

            if not info:
                return jsonify({"error": "No se encontró audio"}), 404

            # Extraemos un enlace directo limpio de audio
            stream_url = info.get('url')
            
            return jsonify({
                "status": "success",
                "title": info.get('title', query),
                "stream_url": stream_url,
                "duration": info.get('duration', 180)
            }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
