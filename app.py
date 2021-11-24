from flask import Flask, jsonify, request, render_template, Response
from flask_cors import CORS
from imutils.video import VideoStream
import imutils
import cv2
import os

app = Flask(__name__)
CORS(app, resources=r'/api/*')
fvc = VideoStream().start()

@app.route('/api/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/', methods=["GET","POST"])
def index():
    if request.method=="GET":
        return render_template('index.html')
    else:        #in case we want to control through post requests
        return

def gen():
    while True:
        frame = fvc.read()
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield ( b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/emotion_lag')
def emotion_lag():
    # emoji = cv2.imread('emoji_images/neutral.png') # Needed in case someone clicks the emoji button before selecting an emotion
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/emotion_swap')
def emotion_swap():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # app.run(debug=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)