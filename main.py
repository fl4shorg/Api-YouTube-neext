from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import yt_dlp
import tempfile
import os

app = FastAPI()

class VideoRequest(BaseModel):
    url: str
    cookies: str  # texto do cookies.txt

@app.post("/info")
def get_video_info(req: VideoRequest):
    try:
        # Criar arquivo temporário com os cookies
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp_cookie:
            tmp_cookie.write(req.cookies)
            tmp_cookie_path = tmp_cookie.name

        # yt-dlp com cookies temporários
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'extract_flat': False,
            'noplaylist': True,
            'cookies': tmp_cookie_path
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(req.url, download=False)

        # Remover arquivo temporário
        os.unlink(tmp_cookie_path)

        # Processar formatos
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