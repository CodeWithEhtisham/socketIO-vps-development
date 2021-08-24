# import cv2
# import numpy as np
# import socket
# import struct
# import threading
# from io import BytesIO

# class Streaming_Video(threading.Thread):
#     def __init__(self, hostname, port):
#         threading.Thread.__init__(self)
#         self.hostname = hostname
#         self.port = port
#         self.running = False
#         self.streaming = False
#         self.jpeg = None

#     def run(self):
#         s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         print('A Socket created')
#         s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#         s.bind((self.hostname, self.port))
#         print('Socket bind complete')
#         payload_size = struct.calcsize("L")
#         s.listen(10)
#         print('Socket is now listening')
#         self.running = True
#         while self.running:
#             print('Searching for Connection')
#             conn, addr = s.accept()
#             print("Connection Accepted")
#             while True:
#                 data = conn.recv(payload_size)
#                 if data:
#                     msg_size = struct.unpack("L", data)[0]
#                     data = b''
#                     while len(data) < msg_size:
#                         missing_data = conn.recv(msg_size - len(data))
#                         if missing_data:
#                             data += missing_data
#                         else:
#                             self.streaming = False
#                             break

#                     if self.jpeg is not None and not self.streaming:
#                         continue
#                     memfile = BytesIO()
#                     memfile.write(data)
#                     memfile.seek(0)
#                     frame = np.load(memfile)
#                     ret, jpeg = cv2.imencode('.jpg', frame)
#                     self.jpeg = jpeg
#                     self.streaming = True
#                 else:
#                     conn.close()
#                     print('Closing connection...')
#                     self.streaming = False
#                     self.running = False
#                     self.jpeg = None
#                     break


#     def stop(self):
#         self.running = False

#     def get_jpeg(self):
#         return self.jpeg.tobytes()

import cv2
import numpy as np
import socket
import struct
import threading
from io import BytesIO
import selectors
sel=selectors.DefaultSelector()
# sel = selectors.DefaultSelectors()
class Streaming_Video(threading.Thread):
    def __init__(self, hostname, port):
        threading.Thread.__init__(self)
        self.hostname = hostname
        self.port = port
        self.running = False
        self.streaming = False
        self.jpeg = None

    def run(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print('A Socket created')
            s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            s.bind((self.hostname, self.port))
            print('Socket bind complete')
            payload_size = struct.calcsize(">L")
            s.listen(10)
            print('Socket is now listening')
            self.running = True
            while self.running:
                print('Searching for Connection')
                conn, addr = s.accept()
                # s.blocking(False)
                s.setblocking(False)
                sel.register(s, selectors.EVENT_READ, data=None)
                print("Connection Accepted")
                while True:
                    data = conn.recv(payload_size)
                    if data:
                        msg_size = struct.unpack(">L", data)[0]
                        data = b''
                        while len(data) < msg_size:
                            # print("len of data",len(data))
                            # print("size of msg ",msg_size)
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
        except Exception as e:
            print("socket error",e)


    def stop(self):
        self.running = False

    def get_jpeg(self):
        return self.jpeg.tobytes()