from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

cookie_path = "cookies.txt"
use_cookies = os.path.exists(cookie_path)

if not use_cookies:
    print("⚠️ cookies.txt não encontrado, continuará sem cookies.")

@app.route('/api/video_info', methods=['GET'])
def video_info():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "Parâmetro 'url' obrigatório."}), 400

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'forcejson': True,
        'extract_flat': False,
        'format': 'bestvideo+bestaudio/best',
    }

    if use_cookies:
        ydl_opts['cookiefile'] = cookie_path

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

            dados = {
                "title": info.get("title"),
                "uploader": info.get("uploader"),
                "thumbnail": info.get("thumbnail"),
                "duration": info.get("duration"),
                "filesize_approx": info.get("filesize_approx"),
                "view_count": info.get("view_count"),
                "formats": []
            }

            for fmt in info.get("formats", []):
                if fmt.get("url"):
                    dados["formats"].append({
                        "format_id": fmt.get("format_id"),
                        "ext": fmt.get("ext"),
                        "resolution": f"{fmt.get('width')}x{fmt.get('height')}" if fmt.get("width") and fmt.get("height") else None,
                        "filesize": fmt.get("filesize"),
                        "url": fmt.get("url")
                    })

            return jsonify(dados)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

handler = app