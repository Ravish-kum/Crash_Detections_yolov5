import torch
import cv2
from pathlib import Path
from centroidtracker import CentroidTracker
ct = CentroidTracker()

model = torch.hub.load('ultralytics/yolov5', 'yolov5s') 
video_path = 'C:\\Users\\ravis\\OneDrive\\Desktop\\Crash_Detections_yolov5\\video11.mp4'
cap = cv2.VideoCapture(video_path)

speed_factor = 1    # speed factor for adjusting speed of frames to be detected
min_width_rectangle = 30    # min  width of rectangle over car
min_height_rectangle = 30   # min height of rectangle over car
start_line_y = 700
count = 0
center_pt_previous_frame = []

def center_and_dimensions(x1, y1, x2, y2):
    '''
    x1 is x co-ordinate of top left corner of box
    x2 is x co-ordinate of bottom right corner of box
    y1 is y co-ordinate of top left corner of box
    y2 is y co-ordinate of bottom right corner of box

    function for finding center , width and height of the box
    '''
    cx = (x1 + x2)/2
    cy = (y1 + y2)/2
    h = y2 - y1
    w = x2 - x1
    return int(cx), int(cy), h, w

while cap.isOpened(): 
    ret, frame = cap.read()
    if not ret:
        print("Error reading frame.")
        break

    count += 1

    # Performing YOLOv5 object detection
    results = model(frame)

    # Getting the detection results for single frame
    detections = results.xyxy[0] 

    desired_classes = ["car", "bike", "truck"]
    conf_threshold = 0.7        # confidence of the object to be the object from the desired class

    # Filter the detections based on the desired classes and confidence threshold
    filtered_detections = [x for x in detections if (x[4] >= conf_threshold) and (model.names[int(x[5])] in desired_classes)]

    center_pt_current_frame =[]
    # forming bounding boxes for the filtered detections
    for box in filtered_detections:
        x1, y1, x2, y2, conf, class_id = box
        
        cx, cy, h, w = center_and_dimensions(x1.item(), y1.item(), x2.item(), y2.item())
        validate_counter = (w >= min_width_rectangle) and (h >= min_height_rectangle)
        if not validate_counter:
            continue

        center_pt_current_frame.append((cx, cy))
        class_name = model.names[int(class_id)]
    
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        cv2.circle(frame, (int(cx),int(cy)), 4, (0, 0, 255), -1)
    

    tracked_dict = ct.register(center_pt_current_frame, center_pt_previous_frame, count)
    
    for object_id, pt in tracked_dict.items():
        cv2.circle(frame, pt, 5, (0,0,225), -1)
        cv2.putText(frame, str(object_id), (pt[0], pt[1] - 7), 0, 1, (0, 0, 255), 2)
    center_pt_previous_frame = center_pt_current_frame.copy()
    # Display the frame with bounding boxes
    cv2.imshow('YOLOv5 Object Detection', frame)

    delay = int(1000 / (speed_factor * cap.get(cv2.CAP_PROP_FPS)))
    if cv2.waitKey(delay) == 13:
        break

cap.release()
cv2.destroyAllWindows()
