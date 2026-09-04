import os
from flask import Flask, request, jsonify
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

    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch1:',
        'source_address': '0.0.0.0'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info and len(info['entries']) > 0:
                info = info['entries'][0]

            audio_url = info.get('url')
            title = info.get('title')
            duration = info.get('duration')

            return jsonify({
                "status": "success",
                "title": title,
                "stream_url": audio_url,
                "duration": duration
            }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
