#!/usr/bin/python3
from flask import Flask, Response, render_template, request, jsonify
import json
import numpy as np
# from cv2 import imread,imdecode,imwrite
import datetime
import base64
from PIL import Image
import io
import sqlite3
# from app import app
import pandas as pd
app = Flask(__name__)
# global flags 
flags=False

def fetchDataframe():
    con = sqlite3.connect("database.db")
    mycursor = con.cursor()
    mycursor.execute(
        "SELECT * from data LEFT JOIN results ON data.frame_id=results.frame_id ORDER by data.frame_id desc limit 100")
    result = mycursor.fetchall()
    con.close()
    # code to split it into 2 lists
    # res1, res2 = map(list, zip(*ini_list))
    df = pd.DataFrame({
        "date": [i[2] for i in result],
        "frame_id": [i[4] for i in result],
        "vehicle": [i[5] for i in result],
        "id": [i[5] for i in result],
        "lable": [i[7] for i in result]})
    return df

def data_check(df, name):
    try:
        return df[name]
    except:
        return 0

def bar_data(df):
    df = df.lable.value_counts()
    return [
        [1, data_check(df, 'Car')],
        [2, data_check(df, "Bus")],
        [3, data_check(df, "Motorcycle")],
        [4, data_check(df, "Van")],
        [5, data_check(df, "Truck")],
        [6, data_check(df, "Bicycle")],
        [7, data_check(df, "Auto_rikshaw")]
    ]

def donut_data(df):
    df = df.lable.value_counts()
    s = sum(df.values)
    if s is 0:
        s = 1
    return [
        {
            'label': 'Car',
            'data': int((data_check(df, "Car")/s)*100),
            'color': '#3c8dbc'
        },
        {
            'label': 'Bus',
            'data': int((data_check(df, "Bus")/s)*100),
            'color': '#0073b7'
        },
        {
            'label': 'Truck',
            'data': int((data_check(df, "Truck")/s)*100),
            'color': '#737CA1'
        },
        {
            'label': 'Bike',
            'data': int((data_check(df, "Bike")/s)*100),
            'color': '#6D7B8D'
        },
        {
            'label': 'Cycle',
            'data': int((data_check(df, "Bicycle")/s)*100),
            'color': '#566D7E'
        },
        {
            'label': 'Rikshaw',
            'data': int((data_check(df, "Auto_rikshaw")/s)*100),
            'color': '#00c0ef'
        },
        {
            'label': "Van",
            'data': int((data_check(df, "Van")/s)*100),
            'color': '#6D7B8D'
        }

    ]

def line_plot(df):
    dt = df[['date', 'id']].groupby(by='date').count()
    d = pd.DatetimeIndex(dt.index)
    year, month, day, hour, minute, second = [], [], [], [], [], []

    for i in d:
        Y = i.year
        M = i.month
        D = i.day
        h = i.hour
        m = i.minute
        s = i.second
        year.append(Y)
        month.append(M)
        day.append(D)
        hour.append(h)
        minute.append(m)
        second.append(s)
    value = [int(i) for i in dt.id.values]
    return year, month, day, hour, minute, second, value, len(dt.id.values)


@app.route("/", methods=['GET', 'POST'])
def index():
    # flags=False
    return render_template("index.html", jsondata=get_json())

@app.route("/history",methods=["GET","POST"])
def history():
    print("history loading")
    if request.method=="POST":
        print("post histoyr")
        print("start datetime",request.form['start'])
        return render_template("history.html",jsondata=get_json())
    else:
        print("get histoyr")
        return render_template("history.html")

def send_result(response=None, error='', status=200):
    if response is None:
        response = {}
    result = json.dumps({'result': response, 'error': error})
    return Response(status=status, mimetype="application/json", response=result)

@app.route('/fetchdata', methods=["POST"])
def get_json():
    global flags
    if flags == False:
        print ("flag false statement")
        df = fetchDataframe()
        bar = bar_data(df)
        donut = donut_data(df)
        print(line_plot(df))
        year, month, day, hour, minute, second, index, ln = line_plot(df)
        flags=True
        return jsonify({
            "bar_data": str(bar),
            "donut_data": donut,
            "year": year,
            "month": month,
            "day": day,
            "hour": hour,
            "minute": minute,
            "second": second,
            "line_index_data": index,
            'count': str(np.random.random(1)),
            "checkflag":False
        })
    else:
        print ("flag true statement")
        df = fetchDataframe()
        bar = bar_data(df)
        donut = donut_data(df)
        print(line_plot(df))
        year, month, day, hour, minute, second, index, ln = line_plot(df)
        return jsonify({
            "bar_data": str(bar),
            "donut_data": donut,
            "year": year,
            "month": month,
            "day": day,
            "hour": hour,
            "minute": minute,
            "second": second,
            "line_index_data": index,
            'count': str(np.random.random(1)),
            "checkflag":True
        })

def db_data_insertion(data):
    try:
        con = sqlite3.connect("database.db")
        sql = "INSERT INTO data(camera_id,camera_loc,capture_time,image_path) VALUES(?,?,?,?)"
        cur = con.cursor()
        cur.execute(sql, data)
        con.commit()
        print("insertiion seccessfull in data table")
        a = cur.lastrowid
        con.close()
        return a
    except Exception as e:
        print("insertion in data table failed :{}".format(e))

def db_results_insertion(data):
    try:
        con = sqlite3.connect("database.db")
        sql = "INSERT INTO results(frame_id,label,prob,x,y,w,h) VALUES(?,?,?,?,?,?,?)"
        cur = con.cursor()
        cur.execute(sql, data)
        con.commit()
        print("insertiion seccessfull in results table")
        con.close()
    except Exception as e:
        print("insertion in result table failed :{}".format(e))

@app.route("/upload", methods=['POST'])
def login():
    if request.method == 'POST':
        try:
            img_str = request.json['image']
            path = request.json["path"]
            camera_id = request.json['camera_id']
            camera_loc = request.json['camera_loc']
            results = request.json['results']
            img_byte=base64.b64decode(img_str.encode('utf-8'))
            img=Image.open(io.BytesIO(img_byte))
            img.save(f"static/img/output.jpg")
            # jpg_original = base64.b64decode(img_str)
            # jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
            # img = imdecode(jpg_as_np, flags=1)
            frame_id = db_data_insertion(
                (camera_id, camera_loc, datetime.datetime.now(), path))
            # imwrite(f"static/img/output.jpg", img)

            for r in results:
                lbl = r['label']
                prob = r['prob']
                x = r['x']
                y = r['y']
                w = r['w']
                h = r['h']
                db_results_insertion((frame_id, lbl, prob, x, y, w, h))

            return send_result("Frame inserted success", status=201)
        except KeyError as e:
            return send_result(error=f'An "image" file is required {e}', status=422)
        except Exception as e:
            return send_result(error=f'Error {e}', status=500)


if __name__ == "__main__":
    app.run(debug=True)
