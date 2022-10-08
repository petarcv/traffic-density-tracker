from flask import Flask, send_from_directory, send_file
from detector import STATE
import json
from threading import Thread
from random import randint
from time import sleep
from stream import run_detector


app = Flask(__name__)

# STATE.update(14, 'alooo')

# def rand_state():
#     while True:
#         STATE.update(randint(0, 15), '')
#         sleep(4)

# t = Thread(target=rand_state)
# t.start()

@app.route("/web/<path:path>")
def index(path):
    if not path:
        path = 'index.html'
    return send_from_directory('web', path)

@app.route('/api/cars')
def read_cars():
    return json.dumps(STATE.get_state())

@app.route('/api/cars.jpg')
def load_image():
    img = STATE.read_curr_img()
    if img is not None:
        return send_file(img, mimetype='img/png')
    raise Exception('ERROR: no image')