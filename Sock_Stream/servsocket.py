import cv2
import numpy as np
import socket
import struct
import threading
from io import BytesIO

class Streaming_Video(threading.Thread):
    def __init__(self, hostname, port):
        threading.Thread.__init__(self)
        self.hostname = hostname
        self.port = port
        self.running = False
        self.streaming = False
        self.jpeg = None

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('A Socket created')
        s.bind((self.hostname, self.port))
        print('Socket bind complete')
        payload_size = struct.calcsize("L")
        s.listen(10)
        print('Socket is now listening')
        self.running = True
        while self.running:
            print('Searching for Connection')
            conn, addr = s.accept()
            print("Connection Accepted")
            while True:
                data = conn.recv(payload_size)
                if data:
                    msg_size = struct.unpack("L", data)[0]
                    data = b''
                    while len(data) < msg_size:
                        missing_data = conn.recv(msg_size - len(data))
                        if missing_data:
                            data += missing_data
                        else:
                            self.streaming = False
                            break

                    if self.jpeg is not None and not self.streaming:
                        continue
                    memfile = BytesIO()
                    memfile.write(data)
                    memfile.seek(0)
                    frame = np.load(memfile)
                    ret, jpeg = cv2.imencode('.jpg', frame)
                    self.jpeg = jpeg
                    self.streaming = True
                else:
                    conn.close()
                    print('Closing connection...')
                    self.streaming = False
                    self.running = False
                    self.jpeg = None
                    break


    def stop(self):
        self.running = False

    def get_jpeg(self):
        return self.jpeg.tobytes()