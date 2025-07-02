from flask import Flask, request, jsonify
import yt_dlp
import os
import traceback

app = Flask(__name__)

cookie_path = os.path.join(os.path.dirname(__file__), "cookies.txt")
use_cookies = os.path.isfile(cookie_path)

if use_cookies:
    print("✅ cookies.txt encontrado. Usando para autenticação.")
else:
    print("⚠️ cookies.txt NÃO encontrado. Algumas URLs podem falhar.")

@app.route('/video_info', methods=['GET'])
def video_info():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "Parâmetro 'url' obrigatório."}), 400

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'forcejson': True,
        'extract_flat': False,
        'format': 'bestvideo+bestaudio/best'
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
        tb = traceback.format_exc()
        return jsonify({
            "error": str(e),
            "traceback": tb
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)