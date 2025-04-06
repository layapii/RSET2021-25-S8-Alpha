from ultralytics import YOLO
import cv2
import numpy as np
class YOLOv11:
    def __init__(self):
        # Load the YOLOv11 model
        self.model = YOLO("yolo11m.pt")

    def detect_objects(self, frame):

        # Convert  BGR to RGB Yolo format
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        results = self.model(image_rgb)  # YOLO model now returns a list of results
        
        # Extract the detected objects
        detected_objects = []
        for result in results:
            for box in result.boxes:
                # Extract the label index and get the class name
                label_idx = int(box.cls)
                label_name = result.names[label_idx]
                detected_objects.append(label_name)
        
        return detected_objects