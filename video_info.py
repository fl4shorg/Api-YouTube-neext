from flask import Flask, request, jsonify
import yt_dlp
import os
import traceback

app = Flask(__name__)

cookie_path = os.path.join(os.path.dirname(__file__), "cookies.txt")
use_cookies = os.path.exists(cookie_path)

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
        'format': 'bestvideo+bestaudio/best',
    }

    if use_cookies:
        ydl_opts["cookiefile"] = cookie_path

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

            resultado = {
                "title": info.get("title"),
                "uploader": info.get("uploader"),
                "thumbnail": info.get("thumbnail"),
                "duration": info.get("duration"),
                "view_count": info.get("view_count"),
                "filesize_approx": info.get("filesize_approx"),
                "formats": []
            }

            for f in info.get("formats", []):
                if f.get("url"):
                    resultado["formats"].append({
                        "format_id": f.get("format_id"),
                        "ext": f.get("ext"),
                        "resolution": f"{f.get('width')}x{f.get('height')}" if f.get("width") else None,
                        "filesize": f.get("filesize"),
                        "url": f.get("url")
                    })

            return jsonify(resultado)

    except Exception as e:
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)