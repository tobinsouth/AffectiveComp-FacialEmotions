from flask import Flask, jsonify, request, session, copy_current_request_context, render_template, Response
from flask_cors import CORS
from imutils.video import VideoStream
from io import StringIO, BytesIO
from PIL import Image
from flask_socketio import SocketIO, send, emit, disconnect
import base64
import numpy as np
import imutils
import cv2
import os
# import socketio

app = Flask(__name__)
# CORS(app)

CORS(app, resources=r'/api/*')
# sio = socketio.Server()
# sio.attach(app)
sio = SocketIO(app, logger = True, engineio_logger = True)

# fvc = VideoStream().start()

@app.route('/api/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/', methods=["GET","POST"])
def index():
    if request.method=="GET":
        return render_template('index.html')
    else:        #in case we want to control through post requests
        return



# def gen():
#     while True:
#         frame = fvc.read()
#         ret, buffer = cv2.imencode('.jpg', frame)
#         frame = buffer.tobytes()
#         yield ( b'--frame\r\n'
#                 b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# @app.route('/video_feed')
# def video_feed():
#     return Response(gen(),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/emotion_lag')
# def emotion_lag():
#     # emoji = cv2.imread('emoji_images/neutral.png') # Needed in case someone clicks the emoji button before selecting an emotion
#     return Response(gen(),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/emotion_swap')
# def emotion_swap():
#     return Response(gen(),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')

@sio.on('message')
def handle_message(message):
    print('received message: ' + message)
    send(message)


@sio.on('my_event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})


@sio.on('my_broadcast_event', namespace='/test')
def test_broadcast_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         broadcast=True)


@sio.on('disconnect_request', namespace='/test')
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']},
         callback=can_disconnect)

@sio.on('sendbitmaptoserver', namespace='/test')
def sendbitmaptoserver(data_image):
    # do something with received client bitmap

    # sbuf = StringIO()
    # sbuf.write(data_image)

    # decode and convert into image
#     b = BytesIO(base64.b64decode(data_image))
#     pimg = Image.open(b)

# #     ## converting RGB to BGR, as opencv standards
#     frame = cv2.cvtColor(np.array(pimg), cv2.COLOR_RGB2BGR)

# #     # Process the image frame
#     frame = imutils.resize(frame, width=700)
#     frame = cv2.flip(frame, 1)
#     imgencode = cv2.imencode('.jpg', frame)[1]

#     # base64 encode
    # stringData = base64.b64encode(data_image).decode('utf-8')
    # b64_src = 'data:image/jpg;base64,'
    # stringData = b64_src + stringData


    # send it back to client (origin)
    emit('sendbitmaptoclient', 
        {'data': data_image}
    )

    # send it back to the other client

    

# @sio.on('vid2ser', namespace='/test')
# def image(data_image):
#     sbuf = StringIO()
#     sbuf.write(data_image)

#     # decode and convert into image
#     b = BytesIO(base64.b64decode(data_image))
#     pimg = Image.open(b)

#     ## converting RGB to BGR, as opencv standards
#     frame = cv2.cvtColor(np.array(pimg), cv2.COLOR_RGB2BGR)

#     # Process the image frame
#     frame = imutils.resize(frame, width=700)
#     frame = cv2.flip(frame, 1)
#     imgencode = cv2.imencode('.jpg', frame)[1]

#     # base64 encode
#     stringData = base64.b64encode(imgencode).decode('utf-8')
#     b64_src = 'data:image/jpg;base64,'
#     stringData = b64_src + stringData

#     # # emit the frame back
#     emit('response_back', stringData)


if __name__ == '__main__':
    # app.run(debug=True)
    sio.run(app, debug=True)

    # port = int(os.environ.get("PORT", 5000))
    # app.run(host='0.0.0.0', port=port)