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

@app.get("/download/youtube")
def download_youtube(url: str = Query(...)):
    try:
        process = stream_video(url)
        return StreamingResponse(
            process.stdout,
            media_type="video/mp4",
            headers={"Content-Disposition": "attachment; filename=video.mp4"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/download/facebook")
def download_facebook(url: str = Query(...)):
    try:
        process = stream_video(url)
        return StreamingResponse(
            process.stdout,
            media_type="video/mp4",
            headers={"Content-Disposition": "attachment; filename=video.mp4"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/download/instagram")
def download_instagram(url: str = Query(...)):
    try:
        process = stream_video(url)
        return StreamingResponse(
            process.stdout,
            media_type="video/mp4",
            headers={"Content-Disposition": "attachment; filename=video.mp4"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/download/twitter")
def download_twitter(url: str = Query(...)):
    try:
        process = stream_video(url)
        return StreamingResponse(
            process.stdout,
            media_type="video/mp4",
            headers={"Content-Disposition": "attachment; filename=video.mp4"}
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
def convert_audio(url: str = Query(...)):
    try:
        ytdlp = subprocess.Popen(
            ['yt-dlp', '-f', 'bestaudio', '-o', '-', url],
            stdout=subprocess.PIPE
        )
        ffmpeg = subprocess.Popen(
            ['ffmpeg', '-i', 'pipe:0', '-vn', '-ab', '128k', '-ar', '44100', '-f', 'mp3', 'pipe:1'],
            stdin=ytdlp.stdout,
            stdout=subprocess.PIPE
        )
        return StreamingResponse(
            ffmpeg.stdout,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=audio.mp3"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))