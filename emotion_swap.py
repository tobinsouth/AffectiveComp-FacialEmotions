import cv2
from helperFuncs import *
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os
from imutils.video import VideoStream
import imutils


debug = False # Use for debugging
emojies = False # Replaces faces with emojis
emoji = cv2.imread('emoji_images/neutral.png') # Needed in case someone clicks the emoji button before selecting an emotion

# Load video
fvs = VideoStream().start()
cv2.namedWindow("Emotion swap")

# Kill a few frames to let the camera adjust
for i in range(5): _ = fvs.read()


# Now we ask for user input to collect emotions of faces
emotions_in_use = [('h', 'happy'), ('s', 'sad'), ('a', 'angry'), ('d', 'disgust'), ('f', 'fear'), ('x', 'surprise'), ('n', 'neutral')]
face_emotions = {}
for key, emotion in emotions_in_use:
    this_emotion_collected = False
    while not this_emotion_collected:
        frame = fvs.read() # Read frame
        frame = imutils.resize(frame, width=450) # Resize for speed
        cv2.putText(frame,'Make a %s face and press key %s' % (emotion, key), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.imshow("Emotion swap", frame) # Display frame

        inputkey = cv2.waitKey(100) & 0xFF # Get user input
        if debug: print('Getting user input', inputkey, ord(key))
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
    frame = imutils.resize(frame, width=450) # Resize for speed
    # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Why are you like this opencv?

    try:
        # Get current face bounds
        (x, y, w, h), _, _ = get_facemask(frame)

        if emojies:
            # Replace face with emoji
            combined_frame = overlay_emoji(emoji, frame, x, y, w, h)
        else:
            # Replace face with previous emotion face
            combined_frame = overlay_face(just_prev_face, just_prev_mask, frame, x, y, w, h)

        cv2.imshow("Emotion swap",combined_frame)

    except ValueError:
        if debug: print("No face detected")
        cv2.imshow("Emotion swap",frame)

    inputkey = cv2.waitKey(1) & 0xFF
    if inputkey == ord('q'):
        break
    if inputkey == ord('e'):
        emojies = not emojies
    for key, emotion in emotions_in_use:
        # Switch to emotion
        if inputkey == ord(key):
            just_prev_face, just_prev_mask = face_emotions[emotion]
            emoji = cv2.imread('emoji_images/%s.png' % emotion, cv2.IMREAD_UNCHANGED)

            # Set emoji background as black bc opencv is weird
            emoji, alpha_layer = emoji[:,:,:3], emoji[:,:,3] 
            emoji[np.stack([alpha_layer]*3, axis = -1) == 0] = 0 # Make 3rd alpha cube to boolean index #WhyIsTobinLikeThis
        
            if emoji is None and debug:
                print('Emoji not found')


cv2.destroyAllWindows()
fvs.stop()
