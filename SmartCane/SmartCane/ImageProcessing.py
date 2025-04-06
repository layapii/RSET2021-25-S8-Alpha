import cv2
from yolov11 import YOLOv11  
import pyttsx3

# Initialize the YOLO detector and text-to-speech engine
detector = YOLOv11()
engine = pyttsx3.init()

def start_detection():
    cap = cv2.VideoCapture(0)  # Start capturing from the default camera
    
    last_detected = ""
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame")
            break
        
        # Detect objects in the current frame
        detected_objects = detector.detect_objects(frame)

        if detected_objects:
            # Join the detected object names into a single string for display
            detected_names = ', '.join(detected_objects)

            # Print detected objects to the terminal
            print(f"Detected: {detected_names}")

            # Display detected names on the frame
            cv2.putText(frame, f"Detected: {detected_names}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Convert new detected objects to speech
            if detected_names != last_detected:
                engine.say(detected_names)
                engine.runAndWait()
                last_detected = detected_names

        # Display the video frame with detections
        cv2.imshow("Smart Cane Object Detection", frame)

        # Press 'q' to stop the detection loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    print("Starting detection...")
    start_detection()
    print("Detection stopped.")

