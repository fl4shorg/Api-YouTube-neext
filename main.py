from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import yt_dlp
import tempfile, os

app = FastAPI()

class VideoRequest(BaseModel):
    url: str
    cookies: str

@app.post("/info")
def get_video_info(req: VideoRequest):
    try:
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp_cookie:
            tmp_cookie.write(req.cookies)
            tmp_cookie_path = tmp_cookie.name

        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'cookies': tmp_cookie_path,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(req.url, download=False)

        os.unlink(tmp_cookie_path)

        return {
            "title": info.get("title"),
            "channel": info.get("uploader"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),
            "formats": [
                {
                    "format_id": f.get("format_id"),
                    "ext": f.get("ext"),
                    "resolution": f.get("height"),
                    "filesize": f.get("filesize"),
                    "url": f.get("url")
                }
                for f in info.get("formats", []) if f.get("url")
            ]
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})