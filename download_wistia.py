from flask import Flask, request, jsonify, render_template_string
import requests
import re

app = Flask(__name__)

def extract_wistia_id(html):
    match = re.search(r'wvideo=([a-zA-Z0-9]+)', html)
    return match.group(1) if match else None

def get_wistia_video_url(video_id):
    api_url = f"https://fast.wistia.com/embed/medias/{video_id}.json"
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        assets = data.get("media", {}).get("assets", [])
        
        for asset in assets:
            if asset.get("type") == "original":  # Get the highest quality video
                return asset.get("url")
        
        return assets[0].get("url") if assets else None
    else:
        return None

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        html_input = request.form.get("html")

        if not html_input:
            return render_template_string(TEMPLATE, error="Missing HTML input")

        wistia_video_id = extract_wistia_id(html_input)

        if wistia_video_id:
            video_url = get_wistia_video_url(wistia_video_id)
            if video_url:
                return render_template_string(TEMPLATE, download_link=video_url)
            else:
                return render_template_string(TEMPLATE, error="Could not retrieve video URL")
        else:
            return render_template_string(TEMPLATE, error="Could not extract Wistia video ID")

    return render_template_string(TEMPLATE)

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Wistia Video Downloader</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            background-color: #f4f4f4;
        }
        .container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        textarea {
            width: 100%;
            height: 100px;
            margin-bottom: 10px;
        }
        button {
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background: #0056b3;
        }
        .error {
            color: red;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Wistia Video Downloader</h2>
        <form method="post">
            <textarea name="html" placeholder="Paste Wistia Embed Code Here"></textarea><br>
            <button type="submit">Get Download Link</button>
        </form>
        {% if download_link %}
            <p><strong>Download Link:</strong> <a href="{{ download_link }}" target="_blank">Click here</a></p>
        {% elif error %}
            <p class="error">Error: {{ error }}</p>
        {% endif %}
    </div>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
