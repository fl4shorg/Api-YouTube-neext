from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import yt_dlp
import os

app = FastAPI()

# Caminho do arquivo cookies.txt (na mesma pasta do código)
COOKIES_FILE = os.path.join(os.path.dirname(__file__), "cookies.txt")

@app.get("/info")
def get_video_info(url: str = Query(..., description="URL do vídeo YouTube")):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': False,
        'noplaylist': True,
        'cookies': COOKIES_FILE
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = []
        for f in info.get("formats", []):
            if not f.get("url"):
                continue
            formats.append({
                "format_id": f.get("format_id"),
                "ext": f.get("ext"),
                "resolution": f.get("resolution") or f.get("height"),
                "filesize": f.get("filesize"),
                "tbr": f.get("tbr"),
                "vcodec": f.get("vcodec"),
                "acodec": f.get("acodec"),
                "url": f.get("url"),
            })

        return JSONResponse({
            "title": info.get("title"),
            "channel": info.get("uploader"),
            "duration": info.get("duration"),
            "thumbnail": info.get("thumbnail"),
            "formats": formats
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})