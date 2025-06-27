from flask import Flask, request, send_file, jsonify, after_this_request
import os
import uuid
import subprocess

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Video to MP3 Converter - Zero Creation™</title>
        <link rel="icon" type="image/jpeg" href="https://i.ibb.co/hRNgjPmS/image.jpg">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Arial', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                color: #333;
                overflow-x: hidden;
            }

            .floating-shapes {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
                z-index: 1;
            }

            .shape {
                position: absolute;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 50%;
                animation: float 6s ease-in-out infinite;
            }

            .shape:nth-child(1) {
                width: 80px;
                height: 80px;
                top: 20%;
                left: 10%;
                animation-delay: 0s;
            }

            .shape:nth-child(2) {
                width: 120px;
                height: 120px;
                top: 60%;
                left: 80%;
                animation-delay: 2s;
            }

            .shape:nth-child(3) {
                width: 60px;
                height: 60px;
                top: 80%;
                left: 20%;
                animation-delay: 4s;
            }

            @keyframes float {
                0%, 100% { transform: translateY(0px) rotate(0deg); }
                50% { transform: translateY(-20px) rotate(180deg); }
            }

            .header {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                padding: 1rem 2rem;
                box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
                position: relative;
                z-index: 10;
            }

            .nav-container {
                max-width: 1200px;
                margin: 0 auto;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .logo {
                display: flex;
                align-items: center;
                gap: 10px;
            }

            .logo img {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                object-fit: cover;
                animation: pulse 2s infinite;
            }

            .logo-text {
                font-size: 1.5rem;
                font-weight: bold;
                background: linear-gradient(45deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }

            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }

            .social-links {
                display: flex;
                gap: 15px;
            }

            .social-btn {
                padding: 8px 15px;
                border-radius: 25px;
                text-decoration: none;
                color: white;
                font-weight: 500;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 0.9rem;
            }

            .whatsapp {
                background: linear-gradient(45deg, #25d366, #128c7e);
            }

            .telegram {
                background: linear-gradient(45deg, #0088cc, #229ed9);
            }

            .social-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
            }

            .main-content {
                flex: 1;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 2rem;
                position: relative;
                z-index: 5;
            }

            .converter-card {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(15px);
                border-radius: 20px;
                padding: 3rem;
                box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
                max-width: 500px;
                width: 100%;
                text-align: center;
                transform: translateY(20px);
                animation: slideUp 0.8s ease forwards;
                position: relative;
                overflow: hidden;
            }

            .converter-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, #667eea, #764ba2);
                border-radius: 20px 20px 0 0;
            }

            @keyframes slideUp {
                to {
                    transform: translateY(0);
                    opacity: 1;
                }
            }

            .card-title {
                font-size: 2.2rem;
                margin-bottom: 0.5rem;
                background: linear-gradient(45deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-weight: bold;
            }

            .card-subtitle {
                color: #666;
                margin-bottom: 2rem;
                font-size: 1.1rem;
            }

            .upload-zone {
                border: 3px dashed #ddd;
                border-radius: 15px;
                padding: 2rem;
                margin-bottom: 2rem;
                transition: all 0.3s ease;
                cursor: pointer;
                position: relative;
            }

            .upload-zone:hover {
                border-color: #667eea;
                background: rgba(102, 126, 234, 0.05);
                transform: scale(1.02);
            }

            .upload-zone.dragover {
                border-color: #764ba2;
                background: rgba(118, 75, 162, 0.1);
                transform: scale(1.05);
            }

            .upload-icon {
                font-size: 3rem;
                color: #667eea;
                margin-bottom: 1rem;
                animation: bounce 2s infinite;
            }

            @keyframes bounce {
                0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
                40% { transform: translateY(-10px); }
                60% { transform: translateY(-5px); }
            }

            .upload-text {
                font-size: 1.1rem;
                color: #555;
                margin-bottom: 0.5rem;
            }

            .upload-hint {
                font-size: 0.9rem;
                color: #888;
            }

            .file-input {
                display: none;
            }

            .convert-btn {
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
                border: none;
                padding: 15px 40px;
                border-radius: 50px;
                font-size: 1.1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
                min-width: 200px;
            }

            .convert-btn:hover:not(:disabled) {
                transform: translateY(-2px);
                box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
            }

            .convert-btn:disabled {
                opacity: 0.7;
                cursor: not-allowed;
            }

            .spinner {
                display: none;
                width: 20px;
                height: 20px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                border-top-color: white;
                animation: spin 1s ease-in-out infinite;
                margin-right: 10px;
            }

            @keyframes spin {
                to { transform: rotate(360deg); }
            }

            .progress-bar {
                display: none;
                width: 100%;
                height: 6px;
                background: #f0f0f0;
                border-radius: 3px;
                margin: 20px 0;
                overflow: hidden;
            }

            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #667eea, #764ba2);
                border-radius: 3px;
                transition: width 0.3s ease;
                width: 0%;
            }

            .result-message {
                margin-top: 20px;
                padding: 15px;
                border-radius: 10px;
                display: none;
            }

            .success {
                background: rgba(76, 175, 80, 0.1);
                color: #4caf50;
                border: 1px solid rgba(76, 175, 80, 0.2);
            }

            .error {
                background: rgba(244, 67, 54, 0.1);
                color: #f44336;
                border: 1px solid rgba(244, 67, 54, 0.2);
            }

            .footer {
                background: rgba(0, 0, 0, 0.8);
                color: white;
                text-align: center;
                padding: 2rem;
                position: relative;
                z-index: 10;
            }

            .footer-content {
                max-width: 1200px;
                margin: 0 auto;
            }

            .footer-brand {
                font-size: 1.2rem;
                margin-bottom: 10px;
                font-weight: bold;
                background: linear-gradient(45deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }

            .footer-text {
                font-size: 0.9rem;
                opacity: 0.8;
            }

            @media (max-width: 768px) {
                .nav-container {
                    flex-direction: column;
                    gap: 15px;
                }

                .social-links {
                    justify-content: center;
                }

                .converter-card {
                    margin: 1rem;
                    padding: 2rem;
                }

                .card-title {
                    font-size: 1.8rem;
                }

                .upload-zone {
                    padding: 1.5rem;
                }
            }
        </style>
    </head>
    <body>
        <div class="floating-shapes">
            <div class="shape"></div>
            <div class="shape"></div>
            <div class="shape"></div>
        </div>

        <header class="header">
            <div class="nav-container">
                <div class="logo">
                    <img src="https://i.ibb.co/hRNgjPmS/image.jpg" alt="Zero Creation">
                    <span class="logo-text">Zero Creation™</span>
                </div>
                <div class="social-links">
                    <a href="https://chat.whatsapp.com/DzEAQVOUQndH8Go17QqYLG" class="social-btn whatsapp" target="_blank">
                        <i class="fab fa-whatsapp"></i>
                        WhatsApp
                    </a>
                    <a href="https://t.me/zerocreations" class="social-btn telegram" target="_blank">
                        <i class="fab fa-telegram"></i>
                        Telegram
                    </a>
                </div>
            </div>
        </header>

        <main class="main-content">
            <div class="converter-card">
                <h1 class="card-title">Video to MP3</h1>
                <p class="card-subtitle">Convert your videos to high-quality MP3 audio files</p>
                
                <form id="convertForm" enctype="multipart/form-data">
                    <div class="upload-zone" id="uploadZone">
                        <i class="fas fa-cloud-upload-alt upload-icon"></i>
                        <div class="upload-text">Choose a video file or drag & drop</div>
                        <div class="upload-hint">Supports MP4, AVI, MOV, MKV and more</div>
                        <input type="file" name="video" accept="video/*" class="file-input" id="fileInput" required>
                    </div>
                    
                    <div class="progress-bar" id="progressBar">
                        <div class="progress-fill" id="progressFill"></div>
                    </div>
                    
                    <button type="submit" class="convert-btn" id="convertBtn">
                        <div class="spinner" id="spinner"></div>
                        <span id="btnText">Convert to MP3</span>
                    </button>
                </form>
                
                <div class="result-message" id="resultMessage"></div>
            </div>
        </main>

        <footer class="footer">
            <div class="footer-content">
                <div class="footer-brand">Powered by Zero • Created by Zero Creation™</div>
                <div class="footer-text">2025© All Rights Reserved</div>
            </div>
        </footer>

        <script>
            const uploadZone = document.getElementById('uploadZone');
            const fileInput = document.getElementById('fileInput');
            const convertForm = document.getElementById('convertForm');
            const convertBtn = document.getElementById('convertBtn');
            const btnText = document.getElementById('btnText');
            const spinner = document.getElementById('spinner');
            const progressBar = document.getElementById('progressBar');
            const progressFill = document.getElementById('progressFill');
            const resultMessage = document.getElementById('resultMessage');

            // Upload zone interactions
            uploadZone.addEventListener('click', () => fileInput.click());

            uploadZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadZone.classList.add('dragover');
            });

            uploadZone.addEventListener('dragleave', () => {
                uploadZone.classList.remove('dragover');
            });

            uploadZone.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadZone.classList.remove('dragover');
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    fileInput.files = files;
                    updateUploadZone(files[0]);
                }
            });

            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    updateUploadZone(e.target.files[0]);
                }
            });

            function updateUploadZone(file) {
                const uploadText = uploadZone.querySelector('.upload-text');
                const uploadIcon = uploadZone.querySelector('.upload-icon');
                
                uploadText.textContent = `Selected: ${file.name}`;
                uploadIcon.className = 'fas fa-file-video upload-icon';
                uploadZone.style.borderColor = '#4caf50';
                uploadZone.style.background = 'rgba(76, 175, 80, 0.05)';
            }

            // Form submission
            convertForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                if (!fileInput.files[0]) {
                    showResult('Please select a video file', 'error');
                    return;
                }

                setLoading(true);
                hideResult();

                const formData = new FormData();
                formData.append('video', fileInput.files[0]);

                try {
                    const response = await fetch('/convert', {
                        method: 'POST',
                        body: formData
                    });

                    if (response.ok) {
                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = fileInput.files[0].name.replace(/\\.[^/.]+$/, '.mp3');
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        window.URL.revokeObjectURL(url);
                        
                        showResult('✅ Conversion successful! Download started.', 'success');
                    } else {
                        const error = await response.json();
                        showResult(`❌ ${error.error || 'Conversion failed'}`, 'error');
                    }
                } catch (error) {
                    showResult(`❌ Network error: ${error.message}`, 'error');
                } finally {
                    setLoading(false);
                }
            });

            function setLoading(loading) {
                convertBtn.disabled = loading;
                spinner.style.display = loading ? 'inline-block' : 'none';
                btnText.textContent = loading ? 'Converting...' : 'Convert to MP3';
                progressBar.style.display = loading ? 'block' : 'none';
                
                if (loading) {
                    simulateProgress();
                } else {
                    progressFill.style.width = '0%';
                }
            }

            function simulateProgress() {
                let progress = 0;
                const interval = setInterval(() => {
                    progress += Math.random() * 15;
                    if (progress > 90) progress = 90;
                    progressFill.style.width = progress + '%';
                    
                    if (!convertBtn.disabled) {
                        progressFill.style.width = '100%';
                        clearInterval(interval);
                    }
                }, 500);
            }

            function showResult(message, type) {
                resultMessage.textContent = message;
                resultMessage.className = `result-message ${type}`;
                resultMessage.style.display = 'block';
                
                setTimeout(() => {
                    resultMessage.style.display = 'none';
                }, 5000);
            }

            function hideResult() {
                resultMessage.style.display = 'none';
            }
        </script>
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
