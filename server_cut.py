import cv2
import mediapipe as mp
import os
import pickle
from collections import deque

os.makedirs('serves', exist_ok=True)

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    enable_segmentation=False,
    smooth_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

filename = 'videos/boy1.mp4'
base_name = os.path.splitext(os.path.basename(filename))[0]

cap = cv2.VideoCapture(filename)
fps = cap.get(cv2.CAP_PROP_FPS)
if not fps or fps <= 0:
    fps = 30
fps = int(fps)

fourcc = cv2.VideoWriter_fourcc(*'mp4v')

seconds = 4
frames = deque(maxlen=fps * seconds)
landmarks_frames = deque(maxlen=fps * seconds)
min_visibility = 0.5
out = None

current_frame = 0
condition1_met = condition2_met = condition3_met = False
saque_count = 0
post_condition3_frames = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    current_frame += 1

    scale_percent = 50
    width = int(frame.shape[1] * scale_percent / 100)
    height = int(frame.shape[0] * scale_percent / 100)
    frame = cv2.resize(frame, (width, height))

    imagem = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(imagem)

    if results.pose_landmarks:
        mp.solutions.drawing_utils.draw_landmarks(
            frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS
        )
        landmarks = results.pose_landmarks.landmark

        landmarks_frames.append(results.pose_landmarks)
        frames.append(frame.copy())

        wrist_visible = landmarks[mp_pose.PoseLandmark.LEFT_WRIST].visibility > min_visibility
        elbow_visible = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].visibility > min_visibility
        shoulder_visible = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].visibility > min_visibility

        # Condição 1: pulso esquerdo acima do nariz (eixo y cresce para baixo)
        if wrist_visible and landmarks[mp_pose.PoseLandmark.LEFT_WRIST].y < landmarks[mp_pose.PoseLandmark.NOSE].y:
            condition1_met = True

        # Condição 2: cotovelo direito acima do ombro direito
        if condition1_met and elbow_visible and shoulder_visible and landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].y < landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y:
            condition2_met = True

        # Condição 3: cotovelo direito abaixo do ombro direito
        if condition2_met and elbow_visible and shoulder_visible and landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].y > landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y:
            condition3_met = True

        if condition3_met:
            post_condition3_frames += 1

        if condition1_met and condition2_met and condition3_met and out is None:
            h, w = frame.shape[:2]
            saque_count += 1
            output_path = os.path.join('serves', f'{base_name}_{saque_count}.mp4')
            out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

        if out is not None and post_condition3_frames >= fps * 2:
            while len(frames) > 0:
                out.write(frames.popleft())
            out.release()
            out = None
            condition1_met = condition2_met = condition3_met = False
            post_condition3_frames = 0

    cv2.imshow('Frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

if out is not None:
    while len(frames) > 0:
        out.write(frames.popleft())
    out.release()

cap.release()
cv2.destroyAllWindows()