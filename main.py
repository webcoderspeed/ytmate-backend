from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import StreamingResponse
import yt_dlp
import subprocess

app = FastAPI()

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

@app.get("/download/youtube")
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

@app.get("/download/facebook")
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

@app.get("/download/vimeo")
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

@app.get("/download/instagram")
def download_instagram(
    url: str = Query(...),
    format: str = Query("best")  # Default to 'best' if not specified
):
    try:
        process = stream_video(url, format)
        # Set media_type and filename based on format (basic logic, can be improved)
        if "jpg" in format or "image" in format:
            media_type = "image/jpeg"
            filename = "image.jpg"
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

@app.get("/download/twitter")
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

@app.get("/download/telegram")
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

@app.get("/convert/audio")
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


@app.get("/convert/hd")
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