# To run this, you need a Raspberry Pi 2 (or greater) with face_recognition and
# the picamera[array] module installed.
# You can follow this installation instructions to get your RPi set up:
# https://gist.github.com/ageitgey/1ac8dbe8572f3f533df6269dab35df65

import face_recognition
from os import listdir
import datetime
import os
import pickle
import time
import cv2
import numpy as np
import math
import utility
import telepot
import pygame

# initialize pygame to reproduce audio files
pygame.mixer.init()

# init bot telegram
bot = telepot.Bot('<your:telegram_bot_token>')

# Initialing PiCamera
# utility.initPiCamera()

# Get vidoe feed from the Camera with opencv
print("Init video capture")
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

encodings = dict()
last_found = dict()
tmp_boxes = list()

# get the haar cascade classifier
face_detection = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

while True:
    # Grab a single frame of video from the Pi camera as a numpy array
    _, img = cap.read()
    
    # mac camera has resolution of 1280*720 -> i have to cut to have a multiple of 640*480
    # doing that i am using the mac camera with the same resolution i will use on the raspbery
    # so i can test it before with my mac and then with the raspberry
    if np.shape(img)[0] == 720 and np.shape(img)[1] == 1280:
        img = img[ :, 160:-160, :] # now i have the same resolution of the pi camera
        img = cv2.flip(img, 1) # flip the image if using frontal camera
    
    # Crop the image with the size i need
    # img = img[100:-140, 160:-160, :]
    
    # Convert color space of the image to gray for detection
    img_detection = cv2.cvtColor(img, cv2.COLOR_RGBA2GRAY)
    
    # get faces bounding box
    faces = face_detection.detectMultiScale(img_detection, scaleFactor=1.3, minNeighbors=5)
       
    # If any face is present perform face recognition
    if len(faces) > 0:
        
        # convert the original image to RGB for face recognition
        img_recognition = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # get normalized css corners (medipipe returns a complex object and has to be transformed)
        css_box = [(y, x + w, y + h, x) for (x, y, w, h) in faces]
        
        # get only boxes where should perform recognition
        boxes_to_compute = list()
        if len(tmp_boxes) == 0:
            tmp_boxes = [utility.Box(face, time.time(), img_recognition) for face in faces]
            boxes_to_compute = tmp_boxes
        else:
            to_add = []
            for face in css_box:
                (top,right,bottom,left) = face
                found = False
                for tmp_box in tmp_boxes:
                    if tmp_box.isCentered(face): 
                        # if a face is on a box check if i have to recognize
                        found = True
                        if tmp_box.shouldRecognize(face):
                            boxes_to_compute.append(tmp_box)

                # if a face is not on any box add it
                if not found:
                    box = utility.Box(face, time.time(), img_recognition)
                    to_add.append(box)
                    boxes_to_compute.append(box)

            tmp_boxes.extend(to_add)
        
        faces_to_compute = [(b.top, b.right, b.bottom, b.left) for b in boxes_to_compute]

        
        # get the face encodings of the recognized data
        face_encodings = face_recognition.face_encodings(img_recognition, faces_to_compute, model="large")

        # Loop over each face found in the frame to see if it's someone we know.
        for i, face_encoding in enumerate(face_encodings):
            
            distances = face_recognition.face_distance(list(encodings.values()), face_encoding)

            name, distance = utility.getClosestName(enumerate(encodings.keys()), distances)
                    
            print("Found one person: {} with distance {}".format(name, distance))

            boxes_to_compute[i].setRecognition(name)

    # removing expired boxes
    to_rm = [b for b in tmp_boxes if b.isExpired()]
    for b in to_rm:
        if  b.name != None and not (b.name in last_found.keys()):
            # welcome newly recognized person
            utility.saluta(b.name)
            # send a message to my bot
            utility.notifyMe(bot, b.name, b.frame)
            last_found[name] = datetime.datetime.now()
        
    tmp_boxes = [b for b in tmp_boxes if not b.isExpired()]
    
    # removes tmp last found elements when expired
    key_to_rm = []
    for key in last_found:
        if key == "unknown":
            if last_found[key] + datetime.timedelta(minutes=1) < datetime.datetime.now():
                key_to_rm.append("unknown")
        elif last_found[key] + datetime.timedelta(minutes=10) < datetime.datetime.now():
            key_to_rm.append(key)

    for key in key_to_rm:
        del last_found[key]

    # updates the encodings
    for f in os.listdir('features'):
        name = f[:-4]
        if name in encodings:
            continue
        with open('features/' + f, 'rb') as n:
            print('Adding features for ' + name)
            encodings[name] = pickle.load(n)
