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
            if asset.get("type") == "original":
                return asset.get("url")
        
        return assets[0].get("url") if assets else None
    return None

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        html_input = request.json.get("html")
        wistia_video_id = extract_wistia_id(html_input)
        
        if wistia_video_id:
            video_url = get_wistia_video_url(wistia_video_id)
            if video_url:
                return jsonify({"download_link": video_url})
            return jsonify({"error": "Could not retrieve video URL"}), 400
        return jsonify({"error": "Could not extract Wistia video ID"}), 400

    return '''
    <form action="/" method="post">
        <textarea name="html" rows="4" cols="50"></textarea><br>
        <input type="submit" value="Get Download Link">
    </form>
    '''

if __name__ == "__main__":
    app.run(debug=True)
