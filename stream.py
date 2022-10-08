import cv2
from picamera2 import Picamera2, Preview, MappedArray
from picamera2.encoders import H264Encoder
import time
from datetime import datetime
import io
import logging
import socketserver
from threading import Condition
from http import server
import imutils
import numpy as np
from RPi import GPIO
from picamera2.encoders import H264Encoder
from detector import STATE

GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)
filesDir = '.'

classNames = []
classFile = filesDir + "/coco.names"
with open(classFile,"rt") as f:
    classNames = f.read().rstrip("\n").split("\n")

configPath = filesDir + "/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightsPath = filesDir + "/frozen_inference_graph.pb"

net = cv2.dnn_DetectionModel(weightsPath,configPath)
net.setInputSize(320,320)
net.setInputScale(1.0/ 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)




def getObjects(img, thres, nms, draw=True, objects=[]):
    classIds, confs, bbox = net.detect(img,confThreshold=thres,nmsThreshold=nms)
    if len(objects) == 0: objects = classNames
    objectInfo =[]
    if len(classIds) != 0:
        for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):
            className = classNames[classId - 1]
            if className in objects:
                objectInfo.append([box,className])
                if (draw):
                    cv2.rectangle(img,box,color=(0,255,0),thickness=2)
                    cv2.putText(img,classNames[classId-1].upper(),(box[0]+10,box[1]+30),
                    cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
                    cv2.putText(img,str(round(confidence*100,2)),(box[0]+200,box[1]+30),
                    cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)

    return img,objectInfo

picam2 = Picamera2()
picam2.start_preview(Preview.QTGL)
config = picam2.create_preview_configuration(main={"size": (1280, 720)}, lores={"size": (320, 240), "format": "YUV420"})
picam2.configure(config)
(w0, h0) = picam2.stream_configuration("main")["size"]
(w1, h1) = picam2.stream_configuration("lores")["size"]
s1 = picam2.stream_configuration("lores")["stride"]
picam2.start()
i = 0

def run_detector():
    while True:
        picam2.capture_file(f"/tmp/cars.jpg")
        img = cv2.imread(f"/tmp/cars.jpg", cv2.IMREAD_COLOR)
        result, cars = getObjects(img,0.45,0.2,draw=False,objects=['car'])
        print(cars)
        if(len(cars) > 0):
            GPIO.output(27, GPIO.HIGH)
            GPIO.output(22, GPIO.HIGH)
            GPIO.output(23, GPIO.HIGH)
        else:
            GPIO.output(27, GPIO.LOW)
            GPIO.output(22, GPIO.LOW)
            GPIO.output(23, GPIO.LOW)
        STATE.update(len(cars), '/tmp/cars.jpg')
        i += 1