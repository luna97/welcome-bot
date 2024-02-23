import telepot
import picamera
import pygame
import time
import threading
import datetime
from PIL import Image
import io

# Function used to notify me when the system srecognize a face
def notifyMe(bot, name, output):
    threading.Thread(target=_notifyMe, args=(bot, name, output)).start()
    
def _notifyMe(bot, name, output):
    try:
        chat = '84217168'
        imgname = "captures/" + name + "_" + str(datetime.datetime.now()) + ".png"
        im = Image.fromarray(output)
        im.save(imgname)
        text = "{} è entrato in casa!".format(name)
        if name == 'unknown':
            text = 'Qualcuno sta entrando in casa!'
        #bot.sendMessage(chat, text)
        bot.sendPhoto(chat, photo=open(imgname, 'rb'), caption=text)
    except Exception as e:
        print("An error occurred sending messages to telegram bot!")
        print(e)

# Function used to say hi to new people
def saluta(name):
    threading.Thread(target=_saluta, args=(name,)).start()
    
def _saluta(name):
    print("I see someone named {}!".format(name))
    if name == "unknown":
        return
    
    pygame.mixer.music.load("saluti/" + name + ".mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue
        
def getCSSCornersMediaPipe(detections):
    css = []
    for d in detections:
        p = d.location_data.relative_bounding_box
        img_height, img_width, _ = np.shape(img)
        top = int(p.ymin * img_height)
        bottom = int((p.ymin + p.height) * img_height)
        left = int(p.xmin * img_width)
        right = int((p.xmin + p.width) * img_width)
        css.append((top, right, bottom, left))
    return css


def getClosestName(names, distances):
    min_val = 1.0
    name = "unknown"
    for index, n in names:
        dist = distances[index]
        if dist <= min_val and dist < 0.55:
            name = n
            min_val = distances[index]
    return (name, min_val)

def initPiCamera():
    print("Init pycamera")
    with picamera.PiCamera() as camera:
        time.sleep(1)
        camera.exposure_mode = 'sports'
        camera.resolution = (640, 480)
        time.sleep(1)
        
class Box:
    def __init__(self, bbox, timestamp, frame, name=None):
        self.update(bbox, timestamp)
        self.name = name
        self.recognized = []
        self.frame = frame
        self.count_detection = 0
        
    def update(self, bbox, timestamp):
        (top,right,bottom,left) = bbox
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left        
        self.timestamp = timestamp
        
    def setRecognition(self, name):
        if name != "unknown" and name in self.recognized:
            self.name = name
            return
        
        self.recognized.append(name)
        if len(self.recognized) > 10:
            # if after 10 attempt cant recognize twice set person as unknown
            self.name = "unknown"
        self.timestamp = time.time()
            
    def isExpired(self):
        return (time.time() - self.timestamp) >= 1
    
    def isCentered(self, bbox):
        (top,right,bottom,left) = bbox
        center = (int(left + ((right - left) / 2)),  int(top + ((bottom - top) / 2)))         
        return center[0] > self.left and center[0] < self.right and center[1] > self.top and center[1] < self.bottom
    
    def shouldRecognize(self, bbox):
        # update values
        self.update(bbox, time.time())
        return self.name == None
    

def is_raspberrypi():
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower(): return True
    except Exception: pass
    return False