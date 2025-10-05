import cv2

print("Testing all camera indices with CAP_AVFOUNDATION...\n")

for i in range(10):
    print(f"Trying camera index {i}...", end=" ")
    cap = cv2.VideoCapture(i, cv2.CAP_AVFOUNDATION)
    
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            h, w = frame.shape[:2]
            print(f"✓ WORKING - Resolution: {w}x{h}")
            
            # Show a preview window
            cv2.imshow(f'Camera {i}', frame)
            cv2.waitKey(1000)  # Show for 1 second
            cv2.destroyAllWindows()
        else:
            print("✓ Opened but can't read frames")
        cap.release()
    else:
        print("✗ Not available")

print("\n" + "="*50)
print("Which camera showed your iPhone? Use that index in main.py")