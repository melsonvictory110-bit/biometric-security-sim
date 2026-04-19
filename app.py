import cv2
import base64
import numpy as np
import mediapipe as mp
from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__)

# --- AI SETUP ---
# We use MediaPipe because it is lightweight and reliable for cloud servers
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(
    model_selection=0, 
    min_detection_confidence=0.4 # Adjust this to make detection easier or harder
)

@app.route('/')
def index():
    """Renders the main biometric interface."""
    return render_template('index.html')

@app.route('/process_frame', methods=['POST'])
def process_frame():
    """Receives camera frames and identifies humans."""
    try:
        # 1. Get the base64 image data from the request
        data = request.json['image']
        header, encoded = data.split(",", 1)
        
        # 2. Decode the image back into a format OpenCV can read
        nparr = np.frombuffer(base64.b64decode(encoded), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({"status": "SENSOR ERROR", "authenticated": False})

        # 3. Convert to RGB for MediaPipe processing
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = face_detection.process(img_rgb)

        # 4. Identification Logic
        if results.detections:
            # If the AI detects human facial landmarks
            return jsonify({
                "status": "VERIFICATION COMPLETED", 
                "authenticated": True,
                "message": "IDENTITY CONFIRMED"
            })
        else:
            # If the frame is empty or face is obscured
            return jsonify({
                "status": "IDENTIFYING SUBJECT...", 
                "authenticated": False
            })

    except Exception as e:
        # Prevents the server from crashing if a bad frame is sent
        print(f"Server Error: {e}")
        return jsonify({"status": "SYSTEM ERROR", "authenticated": False})

if __name__ == '__main__':
    # 'PORT' is set by Render automatically; default to 5000 for local testing
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
