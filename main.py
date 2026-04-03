from flask import Flask, request, render_template_string, jsonify
import replicate
import time
import os

app = Flask(__name__)

# Read API key from environment (or use hardcoded for testing)
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN")

# Full HTML template (complete)
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Media Studio</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: system-ui, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 700px; margin: 0 auto; }
        .header { text-align: center; color: white; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .card {
            background: white;
            border-radius: 24px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        }
        .card h2 { color: #667eea; margin-bottom: 20px; }
        textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            font-size: 16px;
            font-family: inherit;
            resize: vertical;
        }
        button {
            width: 100%;
            background: #667eea;
            color: white;
            border: none;
            padding: 14px;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 15px;
        }
        button:hover { background: #5a67d8; }
        .result { margin-top: 20px; text-align: center; min-height: 200px; }
        .result img { max-width: 100%; border-radius: 12px; }
        .loading { text-align: center; padding: 30px; }
        .loader {
            display: inline-block;
            width: 40px;
            height: 40px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .error { background: #ffe0e0; color: #c33; padding: 12px; border-radius: 12px; }
        .footer { text-align: center; margin-top: 20px; color: white; font-size: 12px; }
        .sample-images { display: flex; gap: 10px; margin-top: 15px; flex-wrap: wrap; }
        .sample-btn {
            background: #f0f0f0;
            padding: 8px 12px;
            border-radius: 20px;
            font-size: 12px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎨 AI Media Studio</h1>
            <p>Generate stunning images with AI — Powered by Flux</p>
        </div>
        <div class="card">
            <h2>🖼️ Image Generator</h2>
            <textarea id="prompt" rows="3" placeholder="Describe what you want to create..."></textarea>
            <div class="sample-images">
                <span class="sample-btn" onclick="setPrompt('A beautiful sunset over mountains')">🌅 Sunset</span>
                <span class="sample-btn" onclick="setPrompt('A cute cat wearing a wizard hat')">🐱 Wizard Cat</span>
                <span class="sample-btn" onclick="setPrompt('A futuristic city with neon lights')">🌆 Futuristic City</span>
                <span class="sample-btn" onclick="setPrompt('A serene lake with mountain reflection')">🏔️ Serene Lake</span>
            </div>
            <button onclick="generate()">✨ Generate Image</button>
            <div id="result" class="result"></div>
        </div>
        <div class="footer">Powered by Replicate • Flux Schnell</div>
    </div>
    <script>
        function setPrompt(text) { document.getElementById('prompt').value = text; }
        async function generate() {
            const prompt = document.getElementById('prompt').value;
            const resultDiv = document.getElementById('result');
            if (!prompt) { alert('Please enter a prompt'); return; }
            resultDiv.innerHTML = '<div class="loading"><div class="loader"></div><p>Creating your image...</p></div>';
            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({prompt: prompt})
                });
                const data = await response.json();
                if (data.success) {
                    resultDiv.innerHTML = `<img src="${data.image_url}" alt="Generated Image">`;
                } else {
                    resultDiv.innerHTML = `<div class="error">❌ ${data.error}</div>`;
                }
            } catch (error) {
                resultDiv.innerHTML = `<div class="error">❌ Error: ${error.message}</div>`;
            }
        }
    </script>
</body>
</html>
"""

@app.route('/generate', methods=['POST'])
def generate():
    prompt = request.json.get('prompt')
    if not prompt:
        return jsonify({'success': False, 'error': 'No prompt'})
    try:
        output = client.run(
            "black-forest-labs/flux-schnell",
            input={
                "prompt": prompt,
                "num_outputs": 1,
                "aspect_ratio": "1:1"
            }
        )
        # output is a list of FileOutput objects, but indexing gives URL string
        image_url = output[0].url
        return jsonify({'success': True, 'image_url': image_url})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
