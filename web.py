from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
load_dotenv()

# Environment variables
API_URL = os.getenv("HUGGING_FACE_API_URL")
API_KEY = os.getenv("HUGGING_FACE_API_KEY")
FLASK_ENV = os.getenv("FLASK_ENV", "development")
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"

# Validate required environment variables
if not API_URL or not API_KEY:
    raise ValueError("HUGGING_FACE_API_URL and HUGGING_FACE_API_KEY must be set in .env file")

if API_KEY == "hf_your_new_api_key_here":
    raise ValueError("Please replace 'hf_your_new_api_key_here' with your actual Hugging Face API key")

# Flask app configuration
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# --- Helper Functions ---
def query_huggingface_api(image_bytes):
    """
    Query the Hugging Face API with image data
    """
    try:
        # Use proper content-type for image data
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/octet-stream"
        }
        
        response = requests.post(
            API_URL, 
            headers=headers, 
            data=image_bytes,
            timeout=30
        )
        
        logger.info(f"API Response Status: {response.status_code}")
        logger.info(f"API Response Headers: {dict(response.headers)}")
        
        # Log response text for debugging 400 errors
        if response.status_code == 400:
            logger.error(f"400 Error Response: {response.text}")
        
        return response
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        raise

def process_api_response(response):
    """
    Process and validate the API response
    """
    # Check status code
    if response.status_code == 503:
        return {
            "error": "Model is currently loading. Please try again in a few minutes.",
            "status_code": response.status_code
        }
    
    if response.status_code == 401:
        return {
            "error": "Invalid API key. Please check your Hugging Face API key.",
            "status_code": response.status_code
        }
    
    if response.status_code == 400:
        logger.error(f"400 Error details: {response.text}")
        return {
            "error": "Bad request. The image format or request structure is invalid.",
            "status_code": response.status_code,
            "details": response.text
        }
    
    if response.status_code != 200:
        return {
            "error": f"API request failed with status {response.status_code}",
            "status_code": response.status_code,
            "details": response.text
        }
    
    # Try to parse JSON response
    try:
        data = response.json()
        logger.info(f"Parsed API Response: {data}")
        
        # Check for API-level errors
        if isinstance(data, dict) and "error" in data:
            return {
                "error": f"API Error: {data['error']}",
                "status_code": response.status_code
            }
        
        return data
        
    except ValueError as e:
        logger.error(f"JSON parsing failed: {str(e)}")
        return {
            "error": "Invalid JSON response from API",
            "status_code": response.status_code,
            "details": response.text
        }

def format_predictions(predictions):
    """
    Format predictions for display
    """
    if not isinstance(predictions, list):
        return predictions
    
    formatted_results = []
    for prediction in predictions:
        if isinstance(prediction, dict):
            label = prediction.get('label', 'Unknown')
            score = prediction.get('score', 0)
            
            # Handle potential None values
            if label is None:
                label = 'Unknown'
            if score is None:
                score = 0
                
            formatted_results.append({
                'label': str(label),
                'score': float(score),
                'percentage': f"{float(score) * 100:.2f}%"
            })
    
    return formatted_results

# --- Flask Routes ---
@app.route('/')
def index():
    """
    Render the main page
    """
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    """
    Handle file upload and image classification
    """
    try:
        # Validate file upload
        if 'file1' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
            
        file = request.files['file1']
        
        if file.filename == '' or file.filename is None:
            return jsonify({"error": "No file selected"}), 400
        
        # Validate file type with better error handling
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
        
        # Check if filename contains a dot
        if '.' not in file.filename:
            return jsonify({
                "error": "File must have an extension. Supported types: " + ', '.join(allowed_extensions)
            }), 400
        
        file_extension = file.filename.rsplit('.', 1)[-1].lower()
        
        if not file_extension or file_extension not in allowed_extensions:
            return jsonify({
                "error": f"Unsupported file type: {file_extension}. Supported types: {', '.join(allowed_extensions)}"
            }), 400
        
        # Read image data
        image_bytes = file.read()
        
        if len(image_bytes) == 0:
            return jsonify({"error": "Empty file uploaded"}), 400
        
        logger.info(f"Processing file: {file.filename} ({len(image_bytes)} bytes)")
        logger.info(f"File extension: {file_extension}")
        
        # Query Hugging Face API
        response = query_huggingface_api(image_bytes)
        
        # Process API response
        result = process_api_response(response)
        
        # Check for errors
        if isinstance(result, dict) and "error" in result:
            return jsonify(result), 500
        
        # Format predictions
        formatted_result = format_predictions(result)
        
        return jsonify(formatted_result)
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            "error": "An unexpected error occurred",
            "details": str(e)
        }), 500

@app.route('/health')
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        "status": "healthy",
        "api_url": API_URL,
        "timestamp": "2025-07-08 14:56:08"
    })

# --- Error Handlers ---
@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "File too large. Maximum size is 16MB."}), 413

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({"error": "Internal server error"}), 500

# --- Run Application ---
if __name__ == '__main__':
    logger.info(f"Starting Flask app...")
    logger.info(f"API URL: {API_URL}")
    logger.info(f"Debug mode: {FLASK_DEBUG}")
    
    app.run(
        host='0.0.0.0', 
        port=81, 
        debug=FLASK_DEBUG
    )