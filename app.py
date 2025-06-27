import os
import tempfile
import uuid
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import subprocess
import logging
from werkzeug.utils import secure_filename
import mimetypes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for web apps

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
UPLOAD_FOLDER = tempfile.mkdtemp()
ALLOWED_VIDEO_EXTENSIONS = {
    'mp4', 'avi', 'mov', 'mkv', 'webm', 'flv', 'wmv', 
    'm4v', '3gp', 'ogv', 'ts', 'mts', 'm2ts'
}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS

def convert_video_to_mp3(input_path, output_path):
    """Convert video file to MP3 using ffmpeg"""
    try:
        # FFmpeg command for video to MP3 conversion
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-vn',  # Disable video
            '-acodec', 'mp3',
            '-ab', '192k',  # Audio bitrate
            '-ar', '44100',  # Sample rate
            '-f', 'mp3',
            output_path,
            '-y'  # Overwrite output file
        ]
        
        # Run FFmpeg command
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            logger.error(f"FFmpeg error: {result.stderr}")
            return False, f"Conversion failed: {result.stderr}"
        
        return True, "Conversion successful"
    
    except subprocess.TimeoutExpired:
        return False, "Conversion timeout - file too large or complex"
    except Exception as e:
        logger.error(f"Conversion error: {str(e)}")
        return False, f"Conversion error: {str(e)}"

@app.route('/', methods=['GET'])
def home():
    """API documentation endpoint"""
    return jsonify({
        "message": "Video to MP3 Converter API",
        "version": "1.0.0",
        "endpoints": {
            "POST /convert": "Convert video file to MP3",
            "GET /health": "Health check"
        },
        "supported_formats": list(ALLOWED_VIDEO_EXTENSIONS),
        "max_file_size": "100MB"
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "API is running"
    })

@app.route('/convert', methods=['POST'])
def convert_video():
    """Convert uploaded video file to MP3"""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({
                "error": "No file provided",
                "message": "Please upload a video file"
            }), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                "error": "No file selected",
                "message": "Please select a video file"
            }), 400
        
        # Check file extension
        if not allowed_file(file.filename):
            return jsonify({
                "error": "Invalid file format",
                "message": f"Supported formats: {', '.join(ALLOWED_VIDEO_EXTENSIONS)}"
            }), 400
        
        # Generate unique filename
        unique_id = str(uuid.uuid4())
        original_filename = secure_filename(file.filename)
        input_filename = f"{unique_id}_{original_filename}"
        output_filename = f"{unique_id}_{os.path.splitext(original_filename)[0]}.mp3"
        
        input_path = os.path.join(UPLOAD_FOLDER, input_filename)
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)
        
        # Save uploaded file
        file.save(input_path)
        logger.info(f"File saved: {input_path}")
        
        # Convert video to MP3
        success, message = convert_video_to_mp3(input_path, output_path)
        
        # Clean up input file
        try:
            os.remove(input_path)
        except OSError:
            pass
        
        if not success:
            return jsonify({
                "error": "Conversion failed",
                "message": message
            }), 500
        
        # Check if output file exists
        if not os.path.exists(output_path):
            return jsonify({
                "error": "Output file not found",
                "message": "Conversion completed but output file missing"
            }), 500
        
        # Return the MP3 file
        return send_file(
            output_path,
            as_attachment=True,
            download_name=f"{os.path.splitext(original_filename)[0]}.mp3",
            mimetype='audio/mpeg'
        )
    
    except Exception as e:
        logger.error(f"Conversion endpoint error: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }), 500

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({
        "error": "File too large",
        "message": "Maximum file size is 100MB"
    }), 413

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors"""
    return jsonify({
        "error": "Internal server error",
        "message": "Something went wrong on our end"
    }), 500

if __name__ == '__main__':
    # Ensure FFmpeg is available
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        logger.info("FFmpeg is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("FFmpeg not found. Please install FFmpeg.")
        exit(1)
    
    # Run the app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
