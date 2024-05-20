import streamlit as st
import cv2
import ffmpeg
import numpy as np
from PIL import Image
import base64

class VideoDataExtractor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.probe = ffmpeg.probe(file_path)
        self.video_info = next(stream for stream in self.probe['streams'] if stream['codec_type'] == 'video')

    def get_all_frames(self):
        cap = cv2.VideoCapture(self.file_path)
        frames = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
        cap.release()
        return frames

    def get_frame_rate(self):
        return eval(self.video_info['r_frame_rate']) if '/' in self.video_info['r_frame_rate'] else float(self.video_info['r_frame_rate'])

    def get_duration(self):
        return float(self.probe['format']['duration'])

def load_yolo_model():
    net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
    with open("coco.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]
    layer_names = net.getLayerNames()
    unconnected_layers = net.getUnconnectedOutLayers()

    if isinstance(unconnected_layers[0], np.ndarray):
        output_layers = [layer_names[i[0] - 1] for i in unconnected_layers]
    else:
        output_layers = [layer_names[i - 1] for i in unconnected_layers]

    return net, classes, output_layers

def detect_objects(frame, net, output_layers, classes):
    height, width, channels = frame.shape
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    class_ids = []
    confidences = []
    boxes = []
    detected_objects = []  # List to store detected objects' details

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > 0.5:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    for i in range(len(boxes)):
        if i in indices:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            color = (0, 255, 0)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # Add detected object details to the list
            detected_objects.append(label)

    return frame, detected_objects

def cv2_to_base64(cv2_img):
    """Converts an OpenCV image to a base64 string."""
    _, buffer = cv2.imencode('.jpg', cv2_img)
    return base64.b64encode(buffer).decode('utf-8')

def main():
    st.title("Video Frame Extractor and Object Detection")
    uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov", "mkv"])

    if uploaded_file is not None:
        with open("temp_video.mp4", "wb") as f:
            f.write(uploaded_file.getbuffer())

        extractor = VideoDataExtractor("temp_video.mp4")
        frames = extractor.get_all_frames()

        frame_rate = extractor.get_frame_rate()
        duration = extractor.get_duration()

        st.write(f"Extracted {len(frames)} frames from the video.")
        st.write(f"Video Duration: {duration:.2f} seconds")
        st.write(f"Frame Rate: {frame_rate:.2f} frames per second")
        st.write(f"Total Frames: {len(frames)}")

        net, classes, output_layers = load_yolo_model()

        selected_frames = []
        detected_objects_per_frame = []  # List to store detected objects for each frame
        for second in range(int(duration)):
            frame_index = int(second * frame_rate)
            if frame_index < len(frames):
                frame = frames[frame_index]
                detected_frame, detected_objects = detect_objects(frame, net, output_layers, classes)
                selected_frames.append(detected_frame)
                detected_objects_per_frame.append(detected_objects)  # Store detected objects

        st.write('<style>div.row { display: flex; overflow-x: auto; } img { margin-right: 10px; }</style>', unsafe_allow_html=True)
        st.write('<div class="row">', unsafe_allow_html=True)
        for i, (frame, detected_objects) in enumerate(zip(selected_frames, detected_objects_per_frame)):
            st.write(f'<div style="display:inline-block;text-align:center;margin-right:10px;">', unsafe_allow_html=True)
            st.write(f'<img src="data:image/jpeg;base64,{cv2_to_base64(frame)}" alt="Frame {i+1}" style="width:200px;height:auto;"/>', unsafe_allow_html=True)
            st.write(f'<p>{" ".join(detected_objects)}</p>', unsafe_allow_html=True)
            st.write('</div>', unsafe_allow_html=True)
        st.write('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
