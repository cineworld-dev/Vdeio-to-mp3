from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
import yt_dlp
import uuid
import os

app = FastAPI()

@app.post("/api/mp3")
async def upload_video(file: UploadFile = File(...)):
    input_path = f"/tmp/{uuid.uuid4()}{file.filename}"
    output_path = input_path.rsplit(".", 1)[0] + ".mp3"

    with open(input_path, "wb") as f:
        f.write(await file.read())

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([input_path])
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

    return FileResponse(path=output_path, filename="converted.mp3", media_type="audio/mpeg")
