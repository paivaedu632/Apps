from flask import Flask, request, jsonify
import requests
import json
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

@app.route("/download", methods=["POST"])
def download():
    data = request.get_json()
    html_input = data.get("html")
    
    if not html_input:
        return jsonify({"error": "Missing HTML input"}), 400
    
    wistia_video_id = extract_wistia_id(html_input)
    
    if wistia_video_id:
        video_url = get_wistia_video_url(wistia_video_id)
        if video_url:
            return jsonify({"download_link": video_url})
        else:
            return jsonify({"error": "Could not retrieve video URL"}), 404
    else:
        return jsonify({"error": "Could not extract Wistia video ID"}), 400

@app.route("/")
def home():
    return jsonify({"message": "Wistia Downloader is running!"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
