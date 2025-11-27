from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
import os
import base64
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageDraw
import random

# Import our image processor
from image_processor import AdvancedImageProcessor

app = Flask(__name__)
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULTS_FOLDER'] = 'results'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Create directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

# Initialize the art generator
art_generator = AdvancedImageProcessor()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

def process_uploaded_file(file):
    """Process uploaded image file"""
    image = Image.open(file.stream)
    
    # Convert to RGB if necessary
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    return image

# HTML Interface
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Art Generator</title>
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
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .content {
            padding: 30px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }
        
        @media (max-width: 768px) {
            .content {
                grid-template-columns: 1fr;
            }
        }
        
        .upload-section, .result-section {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            border: 2px dashed #dee2e6;
        }
        
        .section-title {
            font-size: 1.5em;
            margin-bottom: 20px;
            color: #495057;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        
        .file-input {
            width: 100%;
            padding: 15px;
            border: 2px dashed #667eea;
            border-radius: 8px;
            background: #f8f9ff;
            margin-bottom: 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .file-input:hover {
            background: #e9ecef;
            border-color: #5a67d8;
        }
        
        .style-selector {
            width: 100%;
            padding: 12px;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            font-size: 16px;
            margin-bottom: 20px;
            background: white;
        }
        
        .style-selector:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
            margin-bottom: 10px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .btn:disabled {
            background: #6c757d;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        .image-preview {
            width: 100%;
            max-height: 300px;
            border-radius: 8px;
            border: 2px solid #dee2e6;
            margin-bottom: 20px;
            display: none;
        }
        
        .result-image {
            width: 100%;
            max-height: 400px;
            border-radius: 8px;
            border: 2px solid #28a745;
            display: none;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .message {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: none;
        }
        
        .success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .styles-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .style-option {
            padding: 10px;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .style-option:hover {
            border-color: #667eea;
            background: #f8f9ff;
        }
        
        .style-option.selected {
            border-color: #667eea;
            background: #667eea;
            color: white;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎨 AI Art Generator</h1>
            <p>Transform your images with AI-powered artistic styles</p>
        </div>
        
        <div class="content">
            <!-- Upload Section -->
            <div class="upload-section">
                <h2 class="section-title">Upload & Style</h2>
                
                <div class="message" id="message"></div>
                
                <input type="file" id="imageInput" accept="image/*" class="file-input">
                
                <div id="imagePreviewContainer">
                    <img id="imagePreview" class="image-preview" alt="Image preview">
                </div>
                
                <h3>Choose Art Style:</h3>
                <div class="styles-grid" id="stylesGrid">
                    <!-- Styles will be loaded here -->
                </div>
                
                <select id="styleSelect" class="style-selector">
                    <!-- Options will be loaded here -->
                </select>
                
                <button id="generateBtn" class="btn" disabled>
                    🎨 Generate Art
                </button>
                
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>Creating your masterpiece...</p>
                </div>
            </div>
            
            <!-- Result Section -->
            <div class="result-section">
                <h2 class="section-title">Your Artwork</h2>
                
                <div id="resultContainer">
                    <img id="resultImage" class="result-image" alt="Generated artwork">
                </div>
                
                <div id="resultInfo" style="display: none;">
                    <p><strong>Style Applied:</strong> <span id="appliedStyle"></span></p>
                    <p><strong>Original Size:</strong> <span id="originalSize"></span></p>
                    <button id="downloadBtn" class="btn">💾 Download Image</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let selectedStyle = 'oil_painting';
        let currentResultImage = null;
        
        // Load available styles
        async function loadStyles() {
            try {
                const response = await fetch('/api/styles');
                const data = await response.json();
                
                if (data.success) {
                    const styles = data.styles;
                    const stylesGrid = document.getElementById('stylesGrid');
                    const styleSelect = document.getElementById('styleSelect');
                    
                    // Clear existing options
                    stylesGrid.innerHTML = '';
                    styleSelect.innerHTML = '';
                    
                    // Populate styles grid and dropdown
                    Object.entries(styles).forEach(([key, value]) => {
                        // Grid option
                        const styleDiv = document.createElement('div');
                        styleDiv.className = 'style-option';
                        styleDiv.textContent = value;
                        styleDiv.dataset.style = key;
                        styleDiv.onclick = () => selectStyle(key, styleDiv);
                        stylesGrid.appendChild(styleDiv);
                        
                        // Dropdown option
                        const option = document.createElement('option');
                        option.value = key;
                        option.textContent = value;
                        styleSelect.appendChild(option);
                    });
                    
                    // Select first style by default
                    if (Object.keys(styles).length > 0) {
                        selectStyle(Object.keys(styles)[0], stylesGrid.firstChild);
                    }
                }
            } catch (error) {
                showMessage('Error loading styles: ' + error.message, 'error');
            }
        }
        
        function selectStyle(style, element) {
            selectedStyle = style;
            
            // Update visual selection
            document.querySelectorAll('.style-option').forEach(opt => {
                opt.classList.remove('selected');
            });
            element.classList.add('selected');
            
            // Update dropdown
            document.getElementById('styleSelect').value = style;
        }
        
        // File input handling
        document.getElementById('imageInput').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = document.getElementById('imagePreview');
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                    document.getElementById('generateBtn').disabled = false;
                };
                reader.readAsDataURL(file);
            }
        });
        
        // Style select change
        document.getElementById('styleSelect').addEventListener('change', function(e) {
            selectedStyle = e.target.value;
            
            // Update grid selection
            document.querySelectorAll('.style-option').forEach(opt => {
                opt.classList.remove('selected');
                if (opt.dataset.style === selectedStyle) {
                    opt.classList.add('selected');
                }
            });
        });
        
        // Generate art
        document.getElementById('generateBtn').addEventListener('click', async function() {
            const fileInput = document.getElementById('imageInput');
            const file = fileInput.files[0];
            
            if (!file) {
                showMessage('Please select an image first!', 'error');
                return;
            }
            
            const loading = document.getElementById('loading');
            const generateBtn = document.getElementById('generateBtn');
            
            // Show loading state
            loading.style.display = 'block';
            generateBtn.disabled = true;
            generateBtn.textContent = 'Generating...';
            
            try {
                const formData = new FormData();
                formData.append('image', file);
                formData.append('style_name', selectedStyle);
                
                const response = await fetch('/api/apply-style', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Display result
                    const resultImage = document.getElementById('resultImage');
                    resultImage.src = data.image;
                    resultImage.style.display = 'block';
                    
                    // Show result info
                    document.getElementById('appliedStyle').textContent = data.style_applied;
                    document.getElementById('originalSize').textContent = data.original_size;
                    document.getElementById('resultInfo').style.display = 'block';
                    
                    currentResultImage = data.image;
                    
                    showMessage(data.message, 'success');
                } else {
                    showMessage(data.error || 'Generation failed!', 'error');
                }
            } catch (error) {
                showMessage('Error: ' + error.message, 'error');
            } finally {
                // Hide loading state
                loading.style.display = 'none';
                generateBtn.disabled = false;
                generateBtn.textContent = '🎨 Generate Art';
            }
        });
        
        // Download result
        document.getElementById('downloadBtn').addEventListener('click', function() {
            if (currentResultImage) {
                const link = document.createElement('a');
                link.href = currentResultImage;
                link.download = 'ai_artwork.png';
                link.click();
            }
        });
        
        function showMessage(text, type) {
            const messageDiv = document.getElementById('message');
            messageDiv.textContent = text;
            messageDiv.className = `message ${type}`;
            messageDiv.style.display = 'block';
            
            // Auto-hide success messages after 5 seconds
            if (type === 'success') {
                setTimeout(() => {
                    messageDiv.style.display = 'none';
                }, 5000);
            }
        }
        
        // Initialize
        loadStyles();
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    """Serve the HTML interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/apply-style', methods=['POST'])
def apply_style():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        file = request.files['image']
        style_name = request.form.get('style_name', 'oil_painting')
        
        if not file or file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type. Only JPG, PNG, GIF allowed."}), 400
        
        # Process the uploaded image
        original_image = process_uploaded_file(file)
        
        # Apply the selected style using our image processor
        styled_image = art_generator.process_image(original_image, style_name)
        
        # Save the result
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        result_filename = f"{style_name}_{timestamp}.png"
        result_path = os.path.join(app.config['RESULTS_FOLDER'], result_filename)
        styled_image.save(result_path, 'PNG')
        
        # Convert to base64 for response
        buffered = BytesIO()
        styled_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({
            "success": True,
            "image": f"data:image/png;base64,{img_str}",
            "filename": result_filename,
            "style_applied": style_name,
            "original_size": f"{original_image.width}x{original_image.height}",
            "message": f"Successfully applied {style_name} effect!"
        })
        
    except Exception as e:
        return jsonify({"error": f"Processing error: {str(e)}"}), 500

@app.route('/api/generate-from-text', methods=['POST'])
def generate_from_text():
    try:
        data = request.json
        prompt = data.get('prompt', 'Abstract art')
        style = data.get('style', 'abstract')
        width = data.get('width', 512)
        height = data.get('height', 512)
        
        # Generate art based on text description
        generated_image = generate_art_from_prompt(prompt, style, width, height)
        
        # Save the result
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        result_filename = f"generated_{style}_{timestamp}.png"
        result_path = os.path.join(app.config['RESULTS_FOLDER'], result_filename)
        generated_image.save(result_path, 'PNG')
        
        # Convert to base64 for response
        buffered = BytesIO()
        generated_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({
            "success": True,
            "image": f"data:image/png;base64,{img_str}",
            "filename": result_filename,
            "prompt": prompt,
            "style": style,
            "message": f"Generated {style} art from: '{prompt}'"
        })
        
    except Exception as e:
        return jsonify({"error": f"Generation error: {str(e)}"}), 500

def generate_art_from_prompt(prompt, style, width, height):
    """Generate artwork from text prompt"""
    # Create a new image
    image = Image.new('RGB', (width, height), 'black')
    draw = ImageDraw.Draw(image)
    
    # Use prompt to seed random generator for consistent results
    seed = sum(ord(c) for c in prompt)
    random.seed(seed)
    
    if style == 'abstract':
        # Create abstract patterns
        for i in range(50):
            color = (
                random.randint(0, 255),
                random.randint(0, 255), 
                random.randint(0, 255)
            )
            x1, y1 = random.randint(0, width), random.randint(0, height)
            x2, y2 = random.randint(0, width), random.randint(0, height)
            draw.line([x1, y1, x2, y2], fill=color, width=random.randint(1, 5))
        
        for i in range(20):
            color = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            )
            x, y = random.randint(0, width), random.randint(0, height)
            size = random.randint(10, 100)
            draw.ellipse([x, y, x+size, y+size], fill=color)
    
    elif style == 'landscape':
        # Create simple landscape
        # Sky gradient
        for y in range(height // 2):
            blue_intensity = int(135 + (y / (height // 2)) * 60)
            draw.line([(0, y), (width, y)], fill=(blue_intensity, 206, 235))
        
        # Sun
        draw.ellipse([width//8, height//8, width//4, height//4], fill=(255, 255, 0))
        
        # Mountains
        draw.polygon([
            (0, height//2), 
            (width//4, height//3), 
            (width//2, height//2)
        ], fill=(139, 137, 137))
        
        draw.polygon([
            (width//2, height//2),
            (width*3//4, height//4),
            (width, height//2)
        ], fill=(169, 169, 169))
        
        # Ground
        for y in range(height//2, height):
            green_intensity = int(34 + ((y - height//2) / (height//2)) * 60)
            draw.line([(0, y), (width, y)], fill=(green_intensity, 139, 34))
    
    elif style == 'geometric':
        # Create geometric patterns
        size = 64
        for x in range(0, width, size):
            for y in range(0, height, size):
                color = (
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255)
                )
                if random.choice([True, False]):
                    draw.rectangle([x, y, x+size, y+size], fill=color)
                else:
                    draw.ellipse([x, y, x+size, y+size], fill=color)
    
    else:
        # Default colorful pattern
        for i in range(100):
            color = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            )
            x, y = random.randint(0, width), random.randint(0, height)
            size = random.randint(5, 50)
            draw.rectangle([x, y, x+size, y+size], fill=color)
    
    return image

@app.route('/api/styles', methods=['GET'])
def get_available_styles():
    """Return list of available artistic styles"""
    return jsonify({
        "success": True,
        "styles": art_generator.get_available_styles()
    })

if __name__ == '__main__':
    print("🎨 Advanced AI Art Generator Starting...")
    print("📍 Server running on: http://localhost:5000")
    print("📁 Upload folder:", app.config['UPLOAD_FOLDER'])
    print("📁 Results folder:", app.config['RESULTS_FOLDER'])
    print("✨ Available Styles:", list(art_generator.get_available_styles().keys()))
    print("-" * 50)
    print("🌐 Open your browser and go to: http://localhost:5000")
    print("-" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)