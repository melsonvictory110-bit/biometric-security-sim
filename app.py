import cv2
import base64
import numpy as np
import mediapipe as mp
from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__)

# Direct MediaPipe setup to avoid the cvzone error
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_frame', methods=['POST'])
def process_frame():
    try:
        data = request.json['image']
        header, encoded = data.split(",", 1)
        nparr = np.frombuffer(base64.b64decode(encoded), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Convert to RGB for MediaPipe
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = face_detection.process(img_rgb)

        if results.detections:
            status = "ACCESS GRANTED"
            auth = True
        else:
            status = "SCANNING..."
            auth = False

        return jsonify({"status": status, "authenticated": auth})
    except Exception as e:
        return jsonify({"status": "SYSTEM ERROR", "authenticated": False})

if __name__== '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
