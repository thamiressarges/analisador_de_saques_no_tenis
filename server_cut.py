import cv2
import mediapipe as mp
import os
import pickle
from collections import deque

mp_pose = mp.solutions.pose
pose = mp.solutions.pose.Pose(static_image_mode=False,
                              model_complexity=1,
                              enable_segmentation=False,
                              smooth_landmarks=True,
                              min_detection_confidence=0.5,
                              min_tracking_confidence=0.5)

filename = 'videos/boy1.mp4'
cap = cv2.VideoCapture(filename)
fps = int(cap.get(cv2.CAP_PROP_FPS))

while cap.isOpened():
    ret, frame = cap.read()

    imagem = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(imagem)

    mp.solutions.drawing_utils.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    cv2.imshow('Frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyWindow()
