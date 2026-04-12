import cv2
from cvzone.FaceDetectionModule import FaceDetector
from flask import Flask, render_template, Response
import time

app = Flask(__name__)
detector = FaceDetector()
video = cv2.VideoCapture(0)

# Variables to track the "Scanning" state
face_scan_start = 0
is_authenticated = False

def gen_frames():
    global face_scan_start, is_authenticated
    
    while True:
        success, img = video.read()
        if not success: break
        
        # Detect face
        img, bboxs = detector.findFaces(img)

        if bboxs:
            if face_scan_start == 0:
                face_scan_start = time.time()
            
            elapsed = time.time() - face_scan_start
            
            if elapsed < 3: # First 3 seconds: Verifying
                status = f"VERIFYING BIOMETRICS... {int((elapsed/3)*100)}%"
                color = (255, 255, 0) # Yellow
                # Draw a "loading" line across the face box
                cv2.line(img, (0, 150), (640, 150), color, 2)
            else: # After 3 seconds: Access Granted
                status = "ACCESS GRANTED: USER VERIFIED"
                color = (0, 255, 0) # Green
                is_authenticated = True
        else:
            # Reset if face leaves the frame
            face_scan_start = 0
            is_authenticated = False
            status = "WAITING FOR TARGET..."
            color = (0, 0, 255) # Red

        # Display the high-tech status text
        cv2.putText(img, status, (40, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)