import dlib
import cv2
import os, numpy as np

# Use trained landmark predictor. dlib and stasm are the two best options here.
predictor_path = "shape_predictor_68_face_landmarks.dat"
if not os.path.isfile(predictor_path):
    os.system("wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2")
    os.system("bunzip2 shape_predictor_68_face_landmarks.dat.bz2")

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(predictor_path)


def get_facemask(frame):
    """
    Good for a spa day or for an affective computing project.

    Input is the frame.

    Output in the bounding box coorindates, the mask and the masked frame (maybe cropped tbc). 
    """

    dets = detector(frame, 1) # Only using first detected face right now. #FUTURE WORK
    if len(dets) == 0:
        # If no face it detected, exit with None rather than raising error.
        raise ValueError("No face detected.")

    marks = predictor(frame, dets[0]).parts()
    points = np.array([[point.x, point.y] for point in marks])

    # Helpful params
    x, y, w, h = cv2.boundingRect(np.array([points], np.int32))
    frame_h, frame_w, frame_d = frame.shape

    # Get face section
    mask = np.zeros((frame_h, frame_w), np.uint8)
    cv2.fillConvexPoly(mask, cv2.convexHull(points), 255)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.erode(mask, kernel)
    face = frame.copy()
    face = cv2.bitwise_and(face, face, mask=mask)

    return (x, y, w, h), mask, face



    # if debug: # for when things get weird
        #     # draw bounding box of the detected face
        #     rect = patches.Rectangle((d.left(), d.top()), d.width(), d.height(), fill=False)
        #     ax.add_patch(rect)

        #     # draw landmarks
        #     ax.scatter([point.x for point in marks], [point.y for point in marks])
        #     # for k, point in enumerate(marks):
        #     #     ax.text(point.x, point.y, k)
    

def overlay_face(just_prev_face, just_prev_mask, frame, x, y, w, h):
    """
    Overlays the face on the frame.

    Inputs:
        prev_face: the previous face to overlay (cropped)
        prev_mask: the previous mask to of face (cropped)
        frame: the frame to overlay the face on
        x, y, w, h: the bounding box coordinates of the face

    Returns: frame with face overlayed.
    """

    ## We could use a perspective transform to warp the old face onto the direction of the new one. For now we will just resize.
    # Use point 1,6,12,17 to get the corners of the face and warp to that
    # matrix = cv2.getPerspectiveTransform(prev_warp_points,[[0, 0], [w, 0], [w, h], [0, h]])  # compute perspective matrix
    # cv2.warpPerspective(img, matrix, (width,height), cv2.INTER_LINEAR,
    
    # Resize the face
    resized_prev_face = cv2.resize(just_prev_face, (w,h))
    resized_prev_mask = cv2.resize(just_prev_mask, (w,h))

    # Set old face on the frame
    frame_h, frame_w, frame_d = frame.shape
    prev_face_frame = np.zeros((frame_h, frame_w, frame_d), dtype=np.uint8)
    prev_face_frame[y:y+h, x:x+w, :] = resized_prev_face
    prev_mask_frame = np.zeros((frame_h, frame_w), dtype=np.uint8)
    prev_mask_frame[y:y+h, x:x+w] = resized_prev_mask

    # Join frames
    not_face = cv2.bitwise_not(prev_mask_frame)
    faceless_frame = cv2.bitwise_and(frame, frame, mask=not_face)
    combined_frame = cv2.bitwise_or(faceless_frame,prev_face_frame)

    return combined_frame

# def transform_face(face_box)