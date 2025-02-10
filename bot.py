from flask import Flask, request, render_template
from flask_cors import CORS  # Importing the CORS module

app = Flask(__name__)

# Enable CORS for all domains
CORS(app)

@app.route("/")
def home():
    return "Flask Server is Running!"

@app.route("/stream")
def stream_video():
    video_id = request.args.get("surl", "")
    if not video_id:
        return "Invalid video ID"
    
    video_url = f"https://www.1024terabox.com/sharing/embed?surl={video_id}"
    return render_template("index.html", video_url=video_url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
