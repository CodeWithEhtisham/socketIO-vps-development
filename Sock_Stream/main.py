from flask import Flask, render_template, Response
from servsocket import Streaming_Video
import time
import pickle
import base64
from PIL import Image
import numpy as np
import cv2
app = Flask(__name__)

def gen():
  stream = Streaming_Video('0.0.0.0', 5555)
  stream.start()
  while True:
    if stream.streaming:
      # frame=pickle.loads(stream.get_jpeg(), fix_imports=True, encoding="bytes")
      # print(frame)
      # frame = frame.decode()
      # print('frame',frame[0:100])
      # img_conv = base64.b64decode(frame)
      # as_np = np.frombuffer(img_conv, dtype=np.uint8)
      # org_im = cv2.imdecode(as_np,flags=1)
      # yield(org_im)
      # print("frame",stream.get_jpeg())
      # print("sleep")
      f = open('2.jpg', 'wb')
      f.write(stream.get_jpeg())
      f.close()
      # print(type(stream.get_jpeg()))
      # image=Image.open(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + stream.get_jpeg() + b'\r\n\r\n')
      # image.save(r"img")
      # time.sleep(4)
      yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + stream.get_jpeg() + b'\r\n\r\n')

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/video_feed')
def video_feed():
  print("hello")
  print("frame ",gen())
  # print(Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame'))
  return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
  # app.run(host='192.168.8.110', threaded=True)
    app.run(host='0.0.0.0',port=4000, threaded=True)