from fastapi import FastAPI, APIRouter, Query, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import subprocess
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  
        "https://ytmate.in",      
        "http://ytmate.in",       
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter()

def stream_video(url: str, format: str = "best"):
    ydl_opts = {
        'format': format,
        'outtmpl': '-',  # Output to stdout
        'quiet': True,
        'noplaylist': True,
    }
    # Use yt-dlp to stream to stdout
    process = subprocess.Popen(
        ['yt-dlp', '-f', format, '-o', '-', url],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return process

def get_youtube_format_code(format_key: str):
    # Map frontend keys to yt-dlp format codes for YouTube
    yt_format_map = {
        "360p": "18",
        "720p": "22",
        "1080p": "137+140",
        "1440p": "271+140",
        "4k": "313+140",
        "mp3": "bestaudio",
    }
    return yt_format_map.get(format_key.lower(), format_key)

def get_facebook_format_code(format_key: str):
    # Map frontend keys to yt-dlp format codes for Facebook
    fb_format_map = {
        "sd": "sd",
        "hd": "hd",
        "mp3": "bestaudio",
    }
    # For Facebook, yt-dlp uses 'sd' and 'hd' as format selectors
    return fb_format_map.get(format_key.lower(), format_key)

@api_router.get("/download/youtube")
def download_youtube(
    url: str = Query(...),
    format: str = Query("best")
):
    try:
        yt_format = get_youtube_format_code(format)
        process = stream_video(url, yt_format)
        if yt_format == "bestaudio" or "mp3" in format or "audio" in format:
            media_type = "audio/mpeg"
            filename = "audio.mp3"
        else:
            media_type = "video/mp4"
            filename = "video.mp4"
        return StreamingResponse(
            process.stdout,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/download/facebook")
def download_facebook(
    url: str = Query(...),
    format: str = Query("best")
):
    try:
        fb_format = get_facebook_format_code(format)
        process = stream_video(url, fb_format)
        if fb_format == "bestaudio" or "mp3" in format or "audio" in format:
            media_type = "audio/mpeg"
            filename = "audio.mp3"
        else:
            media_type = "video/mp4"
            filename = "video.mp4"
        return StreamingResponse(
            process.stdout,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/download/vimeo")
def download_vimeo(
    url: str = Query(...),
    format: str = Query("best")  # Default to 'best' if not specified
):
    try:
        process = stream_video(url, format)
        if "mp3" in format or "audio" in format:
            media_type = "audio/mpeg"
            filename = "audio.mp3"
        else:
            media_type = "video/mp4"
            filename = "video.mp4"
        return StreamingResponse(
            process.stdout,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def get_instagram_format_code(format_key: str):
    # Map frontend keys to yt-dlp format codes for Instagram
    insta_format_map = {
        "mp4-hd": "best",
        "mp4-sd": "worst",
        "jpg-hd": "bestimage",
        "mp3": "bestaudio",
    }
    return insta_format_map.get(format_key.lower(), format_key)

@api_router.get("/download/instagram")
def download_instagram(
    url: str = Query(...),
    format: str = Query("best")
):
    
    try:
        insta_format = get_instagram_format_code(format)
        process = stream_video(url, insta_format)
        # Set media_type and filename based on format (basic logic, can be improved)
        if "jpg" in format or "image" in format:
            media_type = "image/jpeg"
            filename = "image.jpg"
        elif insta_format == "bestaudio" or "mp3" in format or "audio" in format:
            media_type = "audio/mpeg"
            filename = "audio.mp3"
        else:
            media_type = "video/mp4"
            filename = "video.mp4"
        return StreamingResponse(
            process.stdout,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/download/twitter")
def download_twitter(
    url: str = Query(...),
    format: str = Query("best")  # Default to 'best' if not specified
):
    try:
        process = stream_video(url, format)
        if "gif" in format:
            media_type = "image/gif"
            filename = "animation.gif"
        else:
            media_type = "video/mp4"
            filename = "video.mp4"
        return StreamingResponse(
            process.stdout,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/download/telegram")
def download_telegram(url: str = Query(...)):
    try:
        process = stream_video(url)
        return StreamingResponse(
            process.stdout,
            media_type="video/mp4",
            headers={"Content-Disposition": "attachment; filename=video.mp4"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/convert/audio")
def convert_audio(
    url: str = Query(...),
    format: str = Query("mp3"),         # audio format: mp3, aac, wav, ogg
    bitrate: str = Query("128k")        # bitrate: 128k, 320k, etc.
):
    try:
        # Map format to ffmpeg extension and mime type
        ext_map = {
            "mp3":  ("mp3",  "audio/mpeg"),
            "aac":  ("aac",  "audio/aac"),
            "wav":  ("wav",  "audio/wav"),
            "ogg":  ("ogg",  "audio/ogg"),
        }
        ext, mime = ext_map.get(format, ("mp3", "audio/mpeg"))
        filename = f"audio.{ext}"

        ytdlp = subprocess.Popen(
            ['yt-dlp', '-f', 'bestaudio', '-o', '-', url],
            stdout=subprocess.PIPE
        )
        ffmpeg_cmd = [
            'ffmpeg', '-i', 'pipe:0', '-vn', '-ab', bitrate, '-ar', '44100', '-f', ext, 'pipe:1'
        ]
        ffmpeg = subprocess.Popen(
            ffmpeg_cmd,
            stdin=ytdlp.stdout,
            stdout=subprocess.PIPE
        )
        return StreamingResponse(
            ffmpeg.stdout,
            media_type=mime,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@api_router.get("/convert/hd")
def convert_hd(
    url: str = Query(...),
    format: str = Query("best")  # e.g., 22 for 720p, 137+140 for 1080p, etc.
):
    try:
        process = stream_video(url, format)
        media_type = "video/mp4"
        filename = "video.mp4"
        return StreamingResponse(
            process.stdout,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/info")
def info(
    platform: str = Query(..., description="Platform name, e.g. youtube, instagram, facebook, etc."),
    url: str = Query(..., description="Media URL"),
    format: str = Query("best", description="Format ID")
):
    try:
        # Use yt-dlp to extract info without downloading
        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "forcejson": True,
            "extract_flat": False,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
        
        title = info_dict.get("title", "Ready to download")
        thumbnail = info_dict.get("thumbnail", "/placeholder.svg")
        duration = info_dict.get("duration")
        if duration:
            # Format duration as H:MM:SS
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            seconds = duration % 60
            duration_str = f"{hours}:{minutes:02}:{seconds:02}"
        else:
            duration_str = "Unknown"

        # Improved file size detection
        file_size = None
        matched_format = None
        for f in info_dict.get("formats", []):
            if f.get("format_id") == format or f.get("format_note") == format:
                matched_format = f
                break
        if matched_format:
            file_size = matched_format.get("filesize") or matched_format.get("filesize_approx")
        else:
            # Fallback: pick the largest filesize available
            sizes = [
                f.get("filesize") or f.get("filesize_approx")
                for f in info_dict.get("formats", [])
                if f.get("filesize") or f.get("filesize_approx")
            ]
            if sizes:
                file_size = max(sizes)

        download_url = f"/download/{platform}?url={url}&format={format}"
        return JSONResponse({
            "title": title,
            "thumbnail": thumbnail,
            "duration": duration_str,
            "downloadUrl": download_url,
            "fileSize": file_size,
            "format": format,
        })
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"error": str(e)}
        )


from fastapi import Request
import requests
from fastapi.responses import StreamingResponse

@app.get("/proxy")
def proxy(url: str, request: Request):
    try:
        # Forward the request to the target URL
        r = requests.get(url, stream=True, timeout=10)
        r.raise_for_status()
        # Get content type from the response
        content_type = r.headers.get("content-type", "application/octet-stream")
        return StreamingResponse(
            r.raw,
            media_type=content_type,
            headers={
                "Access-Control-Allow-Origin": "*"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
app.include_router(api_router, prefix="/api")