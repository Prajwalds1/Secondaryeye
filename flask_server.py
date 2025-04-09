# flask_server.py

from flask import Flask, request, jsonify
import os
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return "ESP32-CAM Upload Server is running"

@app.route("/upload", methods=["POST"])
def upload():
    try:
        if not request.data:
            return jsonify({"error": "No image uploaded"}), 400

        now = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{now}.jpg"
        filepath = os.path.join("uploads", filename)

        with open(filepath, "wb") as f:
            f.write(request.data)

        print(f"✅ Image saved: {filename}")
        return jsonify({"status": "success", "filename": filename}), 200

    except Exception as e:
        print("❌ Upload error:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/latest', methods=['GET'])
def latest_image():
    files = sorted(os.listdir(UPLOAD_FOLDER), reverse=True)
    if not files:
        return jsonify({"error": "No images found"}), 404
    return jsonify({"filename": files[0], "url": f"/uploads/{files[0]}"}), 200

@app.route('/uploads/<filename>')
def serve_image(filename):
    return open(os.path.join(UPLOAD_FOLDER, filename), 'rb').read()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
