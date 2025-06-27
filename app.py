from flask import Flask, request, send_file, jsonify, after_this_request
import os
import uuid
import subprocess

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    # Simple HTML upload form
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Video to MP3</title></head>
    <body>
      <h2>Upload Video to Convert to MP3</h2>
      <form action="/convert" method="post" enctype="multipart/form-data">
        <input type="file" name="video" accept="video/*" required>
        <button type="submit">Convert</button>
      </form>
    </body>
    </html>
    '''

@app.route('/convert', methods=['POST'])
def convert():
    if 'video' not in request.files:
        return jsonify({"error": "No video file uploaded"}), 400

    video = request.files['video']
    if video.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save uploaded video
    input_filename = f"{uuid.uuid4().hex}_{video.filename}"
    input_path = os.path.join(UPLOAD_FOLDER, input_filename)
    video.save(input_path)

    # Output mp3 filename
    output_filename = input_filename.rsplit('.', 1)[0] + ".mp3"
    output_path = os.path.join(UPLOAD_FOLDER, output_filename)

    try:
        # Use ffmpeg to convert video to mp3 audio
        # subprocess.call returns exit code, 0 means success
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-vn",  # no video
            "-ab", "192k",
            "-ar", "44100",
            "-f", "mp3",
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return jsonify({"error": "Conversion failed", "details": result.stderr}), 500

        @after_this_request
        def cleanup(response):
            try:
                os.remove(input_path)
                os.remove(output_path)
            except Exception as e:
                print(f"Cleanup error: {e}")
            return response

        return send_file(output_path, as_attachment=True, mimetype="audio/mpeg")

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
