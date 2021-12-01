import cv2
from imutils.video import VideoStream
import imutils
from helperFuncs import * 

fvs = VideoStream().start()

# fvs = cv2.VideoCapture(0)
# cv2.namedWindow("Emotion lag")

def gen_frames():  

    while True:
            # Read frame
            success, frame = fvs.read()
            # frame = imutils.resize(frame, width=450) # Resize for speed
            if not success:
                print("no success")
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield ( b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
