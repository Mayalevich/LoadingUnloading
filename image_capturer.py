#use this file to take pictures of your object through your webcam

import cv2
import os
import re


def get_latest_count(directory):
    pattern = re.compile(r'img_(\d+)\.jpg')
    max_num = -1
    for filename in os.listdir(directory):
        match = pattern.match(filename)
        if match:
            num = int(match.group(1))
            if num > max_num:
                max_num = num
    return max_num + 1  # Start at next number

cap = cv2.VideoCapture(0)
cap.set(3, 1920)  # Width
cap.set(4, 1080)  # Height
save_dir = "C:/Users/jliu0/Desktop/nuclear_cv/nuclear-cv-challenge/dataset photos"
os.makedirs(save_dir, exist_ok=True)
count = get_latest_count(save_dir)
print("Press C to capture image")



while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow("Capture", frame)
    key = cv2.waitKey(1)

    if key == ord('c'):  # Press 'c' to capture
        cv2.imwrite(f"{save_dir}/img_{count:04d}.jpg", frame)
        print(f"Saved img_{count:04d}.jpg")
        count += 1

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
