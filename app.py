import cv2
import base64
import numpy as np
import mediapipe as mp
from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__)

# Initialize MediaPipe Face Detection
mp_face_detection = mp.solutions.face_detection
# Sensitivity set to 0.3 to make verification easier in different lighting
face_detection = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.3)

@app.route('/')
def index():
    # This looks for the index.html inside your 'templates' folder
    return render_template('index.html')

@app.route('/process_frame', methods=['POST'])
def process_frame():
    try:
        # 1. Receive the base64 image from the HTML/JavaScript
        data = request.json['image']
        header, encoded = data.split(",", 1)
        
        # 2. Convert base64 string back into an actual image
        nparr = np.frombuffer(base64.b64decode(encoded), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # 3. Process image with MediaPipe (requires RGB format)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = face_detection.process(img_rgb)

        # 4. Logic: If a face is detected, Access Granted
        if results.detections:
            status = "ACCESS GRANTED"
            auth = True
        else:
            status = "SCANNING..."
            auth = False

        return jsonify({"status": status, "authenticated": auth})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "SYSTEM ERROR", "authenticated": False})

if __name__ == '__main__':
    # Render requires the app to run on a specific port
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
