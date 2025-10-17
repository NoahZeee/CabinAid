import cv2
import numpy as np
import urllib.request
import threading
import time
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from wifi_communicator import WiFiCommunicator, OutMessage

#for camera
url = 'http://192.168.80.27/cam-hi.jpg'
cap = cv2.VideoCapture(url)
whT = 320
confThreshold = 0.5
nmsThreshold = 0.3
classesfile = 'coco.names'
classNames = []

with open(classesfile, 'rt') as f:
    classNames = f.read().rstrip('\n').split('\n')

modelConfig = 'yolov3.cfg'
modelWeights = 'yolov3.weights'

net = cv2.dnn.readNetFromDarknet(modelConfig, modelWeights)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

# Shared list to store detected items
detected_items = set()
communicator = WiFiCommunicator(max_buffer_sz=128)
lock = threading.Lock()  # Add a lock for thread safety

def findObject(outputs, im):
    hT, wT, cT = im.shape
    bbox = []
    classIds = []
    confs = []
    global detected_items

    # keeping recording
    temp_detected = set()

    for output in outputs:
        for det in output:
            scores = det[5:]
            classId = np.argmax(scores)
            confidence = scores[classId]
            if confidence > confThreshold:
                w, h = int(det[2]*wT), int(det[3]*hT)
                x, y = int((det[0]*wT)-w/2), int((det[1]*hT)-h/2)
                bbox.append([x, y, w, h])
                classIds.append(classId)
                confs.append(float(confidence))

    indices = cv2.dnn.NMSBoxes(bbox, confs, confThreshold, nmsThreshold)

    with lock:  # Thread-safe update
        for i in indices:
            i = i[0] if isinstance(i, (list, tuple, np.ndarray)) else i
            box = bbox[i]
            x, y, w, h = box
            label = classNames[classIds[i]]
            temp_detected.add(label)

            cv2.rectangle(im, (x, y), (x + w, y + h), (255, 0, 255), 2)
            cv2.putText(im, f'{label.upper()} {int(confs[i] * 100)}%', (x, y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)

        detected_items.clear()
        detected_items.update(temp_detected)

def camera_loop():
    while True:
        try:
            img_resp = urllib.request.urlopen(url)
            imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
            im = cv2.imdecode(imgnp, -1)
            blob = cv2.dnn.blobFromImage(im, 1/255, (whT, whT), [0, 0, 0], 1, crop=False)
            net.setInput(blob)
            layernames = net.getLayerNames()
            outputNames = [layernames[i[0] - 1] for i in net.getUnconnectedOutLayers()]
            outputs = net.forward(outputNames)
            findObject(outputs, im)
            cv2.imshow('Camera Detection', im)
            if cv2.waitKey(1) == ord('q'):
                break
        except Exception as e:
            print(f"Camera loop error: {e}")

    cap.release()
    cv2.destroyAllWindows()

# web server
app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('item.html')

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    user_input = data.get('input', '').lower().strip()
    communicator.send_message(OutMessage('p')) #sends p to esp32 when pressed
    found = False
    timeout = 6  # seconds it takes
    start_time = time.time()

    while time.time() - start_time < timeout:
        with lock:
            if user_input in detected_items:
                found = True
                break
        time.sleep(0.1)  

    if found:
        message = user_input + " is found in storage space"
    else:
        message = user_input + " is not found in storage space"

    return jsonify({'message': message})

def flask_app():
    app.run(debug=False, port=5000)

#main program
if __name__ == "__main__":
    threading.Thread(target=camera_loop, daemon=True).start()
    flask_app()
