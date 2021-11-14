import cv2
from helperFuncs import *
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os
from imutils.video import VideoStream
import imutils


debug = False

# Load video
fvs = VideoStream().start()
cv2.namedWindow("Emotion swap")

# Kill a few frames to let the camera adjust and collect prams
for i in range(5): _ = fvs.read()


# Now we ask for user input to collect emotions of faces
emotions_in_use = [('h', 'happy'), ('s', 'sad'), ('a', 'angry'), ('d', 'disgust'), ('f', 'fear'), ('n', 'neutral'), ('t', 'surprise')]
face_emotions = {}
for key, emotion in emotions_in_use:
    this_emotion_collected = False
    while not this_emotion_collected:
        frame = fvs.read() # Read frame
        frame = imutils.resize(frame, width=450)
        cv2.putText(frame,'Make a %s face and press key %s' % (emotion, key), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.imshow("Emotion swap", frame) # Display frame

        inputkey = cv2.waitKey(100) & 0xFF # Get user input
        print('Getting user input', inputkey, ord(key))
        if inputkey == ord(key):
            try: 
                (x, y, w, h), prev_mask, prev_face = get_facemask(frame)
                just_prev_face = prev_face[y:y+h, x:x+w, :]
                just_prev_mask = prev_mask[y:y+h, x:x+w]
                # Save face and mask and move to next emotion
                face_emotions[emotion] = (just_prev_face, just_prev_mask) 
                this_emotion_collected = True
            except ValueError: 
                print('Missing face')

# Loop through to create video
while True:
    # Read frame
    frame = fvs.read()
    frame = imutils.resize(frame, width=450)
    # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Why are you like this opencv?

    try:
        # Get current face bounds
        (x, y, w, h), _, _ = get_facemask(frame)

        combined_frame = overlay_face(just_prev_face, just_prev_mask, frame, x, y, w, h)

        cv2.imshow("Emotion swap",combined_frame)

    except ValueError:
        print("No face detected")
        cv2.imshow("Emotion swap",frame)

    inputkey = cv2.waitKey(1) & 0xFF
    if inputkey == ord('q'):
        break
    for key, emotion in emotions_in_use:
        # Switch to emotion
        if inputkey == ord(key):
            just_prev_face, just_prev_mask = face_emotions[emotion]


cv2.destroyAllWindows()
fvs.release()


       


# # import stasm

# points = stasm.search_single(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
# points = points.astype(np.int32)
# x, y, w, h = cv2.boundingRect(np.array([points], np.int32))
# # boundary_points =  [[x+w, y], [x, y+h]]
# # # points = np.vstack([points, boundary_points])

# plt.scatter(points[:,0], points[:,1]); plt.show()


# mask = np.zeros((frame_h, frame_w), np.uint8)
# cv2.fillConvexPoly(mask, cv2.convexHull(points), 255)
# radius = 5  # kernel size
# kernel = np.ones((radius, radius), np.uint8)
# mask = cv2.erode(mask, kernel)

# plt.imshow("Emotion swap",mask); plt.show()

