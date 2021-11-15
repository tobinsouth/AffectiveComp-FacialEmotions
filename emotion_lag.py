import cv2
from helperFuncs import *
from imutils.video import VideoStream
import imutils


debug = False # Use for debugging
emojies = False # Replaces faces with emojis
emoji = cv2.imread('emoji_images/neutral.png') # Needed in case someone clicks the emoji button before selecting an emotion

# Load video
fvs = VideoStream().start()
cv2.namedWindow("Emotion lag")

# Kill a few frames to let the camera adjust and collect paras

face_queue = []
while len(face_queue) < 10: 
    frame = fvs.read()
    try:
        # Get current face bounds
        (x, y, w, h), prev_mask, prev_face = get_facemask(frame)
        just_prev_face = prev_face[y:y+h, x:x+w, :]
        just_prev_mask = prev_mask[y:y+h, x:x+w]
        face_queue.append((just_prev_face, just_prev_mask))
    except:
        pass
    cv2.putText(frame,'Collecting face queue', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    cv2.imshow("Emotion lag", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break        


# Loop through to create video
while True:
    # Read frame
    frame = fvs.read()
    frame = imutils.resize(frame, width=450) # Resize for speed

    try:
        # Get current face bounds
        (x, y, w, h), prev_mask, prev_face = get_facemask(frame)
        just_prev_face = prev_face[y:y+h, x:x+w, :]
        just_prev_mask = prev_mask[y:y+h, x:x+w]
        face_queue.append((just_prev_face, just_prev_mask))

        just_prev_face, just_prev_mask = face_queue.pop(0)

        # Replace face with previous emotion face
        combined_frame = overlay_face(just_prev_face, just_prev_mask, frame, x, y, w, h)

        cv2.imshow("Emotion lag",combined_frame)

    except ValueError:
        if debug: print("No face detected")
        cv2.imshow("Emotion lag",frame)

    inputkey = cv2.waitKey(1) & 0xFF
    if inputkey == ord('q'):
        break

cv2.destroyAllWindows()
fvs.stop()
