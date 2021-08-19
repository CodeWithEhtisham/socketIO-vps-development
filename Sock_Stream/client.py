import cv2
import numpy as np
import socket
import struct
from io import BytesIO
import pickle
import base64

cap = cv2.VideoCapture(0)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.18.208', 8080))

while cap.isOpened():
    _, frame = cap.read()
    memfile = BytesIO()
    np.save(memfile, frame)
    memfile.seek(0)
    data = memfile.read()

    client_socket.sendall(struct.pack("L", len(data)) + data)
    
    # ret, frame = cam.read()
    # result, img_encode = cv2.imencode('.jpg', frame, encode_param)
    # data = zlib.compress(pickle.dumps(frame, 0))
    # img_encode = cv2.imencode('.jpg', frame)
    # img_encode = base64.b64encode(cv2.imencode('.png', frame)[1])
    # data = pickle.dumps(img_encode, 0)
    # size = len(data)
    # print("{}: {}".format(size))
    # # img_counter+=1
    # client_socket.sendall(struct.pack(">L", size) + data)
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break

cap.release()