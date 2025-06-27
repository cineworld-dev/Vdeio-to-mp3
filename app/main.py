from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
import uuid
import os
import subprocess

app = FastAPI()

@app.get("/")
async def root():
    return {
        "Join": "https://t.me/zerocreations",
        "response": "Welcome to the Video to MP3 Converter API",
        "status": 200,
        "successful": "success"
    }

@app.post("/convert")
async def convert_to_mp3(file: UploadFile = File(...)):
    unique_id = str(uuid.uuid4())
    input_path = f"temp/{unique_id}_{file.filename}"
    output_path = f"temp/{unique_id}.mp3"

    os.makedirs("temp", exist_ok=True)
    with open(input_path, "wb") as f:
        f.write(await file.read())

    try:
        subprocess.run(
            ["ffmpeg", "-i", input_path, "-vn", "-ab", "192k", "-ar", "44100", "-y", output_path],
            check=True
        )
    except subprocess.CalledProcessError:
        return JSONResponse({"error": "Conversion failed"}, status_code=500)

    return FileResponse(output_path, filename="converted.mp3", media_type="audio/mpeg")
