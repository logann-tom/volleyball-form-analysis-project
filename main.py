import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from player_data import PlayerData
import cv2
import math
SCALE = .4
debug = True
padding = 5
# 0 - nose
# 1 - left eye (inner)
# 2 - left eye
# 3 - left eye (outer)
# 4 - right eye (inner)
# 5 - right eye
# 6 - right eye (outer)
# 7 - left ear
# 8 - right ear
# 9 - mouth (left)
# 10 - mouth (right)
# 11 - left shoulder
# 12 - right shoulder
# 13 - left elbow
# 14 - right elbow
# 15 - left wrist
# 16 - right wrist
# 17 - left pinky
# 18 - right pinky
# 19 - left index
# 20 - right index
# 21 - left thumb
# 22 - right thumb
# 23 - left hip
# 24 - right hip
# 25 - left knee
# 26 - right knee
# 27 - left ankle
# 28 - right ankle
# 29 - left heel
# 30 - right heel
# 31 - left foot index
# 32 - right foot index
POSE_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,7),(0,4),(4,5),(5,6),(6,8),
    (9,10),(11,12),(11,13),(13,15),(15,17),(15,19),(15,21),(17,19),
    (12,14),(14,16),(16,18),(16,20),(16,22),(18,20),
    (11,23),(12,24),(23,24),(23,25),(24,26),(25,27),(26,28),
    (27,29),(28,30),(29,31),(30,32),(27,31),(28,32)
]

base_options = python.BaseOptions(model_asset_path='pose_landmarker_heavy.task')
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    output_segmentation_masks=False,
    num_poses = 1
)
landmarker = vision.PoseLandmarker.create_from_options(options)
# Open video and grab first frame for ROI selection
cap = cv2.VideoCapture("media/hit1.mp4")
fps = cap.get(cv2.CAP_PROP_FPS)
ret, first_frame = cap.read()
h, w = first_frame.shape[:2]
# Let user draw a box around the hitter
display_first = cv2.resize(first_frame, (int(w * SCALE), (int (h * SCALE))))
roi = cv2.selectROI("Select the hitter", display_first, fromCenter=False)
cv2.destroyAllWindows()
rx, ry, rw, rh = [int (v/SCALE) for v in roi]
roi_cx = rx + rw / 2
roi_cy = ry + rh / 2
max_drift = rw * .6
box_h = rh + padding
box_w = rw + padding

def closest_pose_to_roi(pose_landmarks_list, w, h, roi_cx, roi_cy):
    best_idx = 0
    best_dist = float('inf')
    for i, landmarks in enumerate(pose_landmarks_list):
        # Use hip midpoint as person center
        lshoulder = landmarks[11]
        rshoulder = landmarks[12]
        lhip = landmarks[23]
        rhip = landmarks[24]
        
        cx = ((lhip.x + rhip.x + lshoulder.x + rshoulder.x) / 4) * w
        cy = ((lhip.y + rhip.y + lshoulder.y + rshoulder.y) / 4) * h
        dist = (cx - roi_cx) ** 2 + (cy - roi_cy) ** 2
        if dist < best_dist:
            best_dist = dist
            best_idx = i
    return best_idx

def _get_dist_2d(p1, p2):
    dx = p1.x - p2.x
    dy = p1.y - p2.y  
    return math.sqrt(dx**2 + dy**2)
def _get_dist_3d(p1,p2):
    dx = p1.x - p2.x
    dy = p1.y - p2.y  
    dz = p1.z - p2.z
    return math.sqrt(dx**2 + dy**2 + dz**2)

paused = False
frame_num = 0
hitter = PlayerData(fps)
while cap.isOpened():
    if not paused:
        ret, frame = cap.read()
        if not ret:
            break
        process_frame = True
    else:
        process_frame = False

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('p'):
        paused = not paused
    elif key == ord('.') and paused:
        ret, frame = cap.read()
        if not ret:
            break
        process_frame = True
    elif key == ord('d'):
        print(frame_num)

    if process_frame:
        frame_num = frame_num + 1
        h, w = frame.shape[:2]
        y_start = max(0, int(roi_cy - box_h/2))
        y_end = min(h, int(roi_cy + box_h/2))
        x_start = max(0, int(roi_cx - box_w/2))
        x_end = min(w, int(roi_cx + box_w/2))
        cropped = frame[y_start:y_end, x_start:x_end]   
        rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = landmarker.detect(mp_image)
        
        
        if result.pose_landmarks:
            lm = result.pose_landmarks[0]
            wlm = result.pose_world_landmarks[0]
            print(f"Frame {frame_num}:")
            print(f"  2D shoulder dist: {_get_dist_2d(lm[11], lm[12]):.3f}")
            print(f"  3D shoulder dist: {_get_dist_3d(wlm[11], wlm[12]):.3f}")
            idx = closest_pose_to_roi(result.pose_landmarks, x_end - x_start, y_end - y_start, (x_end - x_start) / 2, (y_end - y_start) / 2)
            landmarks = result.pose_landmarks[idx]
            crop_w = x_end - x_start
            crop_h = y_end - y_start
            hitter.update(frame_num, landmarks, crop_w, crop_h)

            for lm in landmarks:
                # translate from crop space to full frame space
                full_x = int(x_start + lm.x * (x_end - x_start))
                full_y = int(y_start + lm.y * (y_end - y_start))
                cv2.circle(frame, (full_x, full_y), 4, (0, 0, 255), -1)
            
            for a, b in POSE_CONNECTIONS:
                a_x = int(x_start + landmarks[a].x * (x_end - x_start))
                a_y = int(y_start + landmarks[a].y * (y_end - y_start))
                b_x = int(x_start + landmarks[b].x * (x_end - x_start))
                b_y = int(y_start + landmarks[b].y * (y_end - y_start))
                cv2.line(frame,(a_x,a_y), (b_x,b_y), (0, 255, 0),3)
                    

            lshoulder, rshoulder = landmarks[11], landmarks[12]
            lhip, rhip = landmarks[23], landmarks[24]

            new_cx = x_start + ((lshoulder.x + rshoulder.x + lhip.x + rhip.x) / 4) * (x_end - x_start)
            new_cy = y_start + ((lshoulder.y + rshoulder.y + lhip.y + rhip.y) / 4) * (y_end - y_start)

            dist = ((new_cx - roi_cx)**2 + (new_cy - roi_cy)**2) ** 0.5
            if dist < max_drift:
                roi_cx = new_cx
                roi_cy = new_cy

            if debug:
                cv2.circle(frame, (int(roi_cx), int(roi_cy)), 10, (255, 0, 0), -1)
                cv2.rectangle(frame, (x_start, y_start), (x_end, y_end), (255, 0, 0), 2)

        display = cv2.resize(frame, (int(w * SCALE), int(h * SCALE)))
        cv2.imshow("Pose", display)

print(hitter.getAllMetrics())