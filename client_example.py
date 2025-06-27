import requests
import os

# API Configuration
API_BASE_URL = "https://your-railway-app.railway.app"  # Replace with your Railway URL

def convert_video_to_mp3(video_file_path, output_path=None):
    """
    Convert a video file to MP3 using the API
    
    Args:
        video_file_path (str): Path to the input video file
        output_path (str): Path where to save the MP3 file (optional)
    
    Returns:
        bool: True if successful, False otherwise
    """
    
    # Check if input file exists
    if not os.path.exists(video_file_path):
        print(f"Error: File {video_file_path} not found")
        return False
    
    # Prepare the file for upload
    with open(video_file_path, 'rb') as file:
        files = {'file': file}
        
        try:
            print(f"Uploading and converting {video_file_path}...")
            
            # Make API request
            response = requests.post(
                f"{API_BASE_URL}/convert",
                files=files,
                timeout=300  # 5 minute timeout
            )
            
            if response.status_code == 200:
                # Determine output filename
                if output_path is None:
                    base_name = os.path.splitext(os.path.basename(video_file_path))[0]
                    output_path = f"{base_name}.mp3"
                
                # Save the MP3 file
                with open(output_path, 'wb') as output_file:
                    output_file.write(response.content)
                
                print(f"✅ Conversion successful! MP3 saved as: {output_path}")
                return True
            
            else:
                error_data = response.json()
                print(f"❌ Error: {error_data.get('message', 'Unknown error')}")
                return False
                
        except requests.exceptions.Timeout:
            print("❌ Error: Request timeout - file might be too large")
            return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Error: Network error - {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False

def check_api_health():
    """Check if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ API is healthy")
            return True
        else:
            print("❌ API health check failed")
            return False
    except Exception as e:
        print(f"❌ Cannot reach API: {str(e)}")
        return False

def get_api_info():
    """Get API information"""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=10)
        if response.status_code == 200:
            info = response.json()
            print("📋 API Information:")
            print(f"   Version: {info.get('version')}")
            print(f"   Supported formats: {', '.join(info.get('supported_formats', []))}")
            print(f"   Max file size: {info.get('max_file_size')}")
            return True
        else:
            print("❌ Cannot get API info")
            return False
    except Exception as e:
        print(f"❌ Cannot reach API: {str(e)}")
        return False

# Example usage
if __name__ == "__main__":
    # Update this with your Railway app URL
    API_BASE_URL = "https://your-railway-app.railway.app"
    
    print("🎵 Video to MP3 Converter Client")
    print("=" * 40)
    
    # Check API health
    if not check_api_health():
        print("Please check your API URL and make sure the service is running")
        exit(1)
    
    # Get API information
    get_api_info()
    print()
    
    # Example conversion
    video_file = "example_video.mp4"  # Replace with your video file
    
    if os.path.exists(video_file):
        convert_video_to_mp3(video_file)
    else:
        print(f"Please provide a valid video file path. '{video_file}' not found.")
        
        # Interactive mode
        while True:
            file_path = input("\nEnter video file path (or 'quit' to exit): ").strip()
            if file_path.lower() == 'quit':
                break
            if file_path:
                convert_video_to_mp3(file_path)
