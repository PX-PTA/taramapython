# PENGGUNAAN
# python face-recognition-video.py --cascade haarcascade_frontalface_default.xml --encodings encodings.pickle

# import library yang di perlukan
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2
import time
import requests
import os
import os.path
from os import path

try:
    import httplib
except:
    import http.client as httplib
    
# Parsing Argumen
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--cascade", required=True,
    help = "path to where the face cascade resides")
ap.add_argument("-e", "--encodings", required=True,
    help="path to serialized db of facial encodings")
args = vars(ap.parse_args())

# load pendeteksi wajah dari file cascade OpenCV
print("[INFO] loading encodings + face detector...")
data = pickle.loads(open(args["encodings"], "rb").read())
detector = cv2.CascadeClassifier(args["cascade"])

# Nyalakan Kamera
print("[INFO] Memulai Stream dari Pi Camera...")
vs = VideoStream(src=0).start()
time.sleep(2.0)

# Penghitung FPS (Frame per Second)
fps = FPS().start()

ipAddress = "192.168.1.7/tarama"
# define the access rights
access_rights = 0o755

def checkInternetHttplib(url, timeout=3):
    conn = httplib.HTTPConnection(url="www.google.com", timeout=timeout)
    try:
        conn.request("HEAD", "/")
        conn.close()
        return True
    except Exception as e:
        print(e)
        return False

def getDevice():
    r = requests.get('http://192.168.1.7/tarama/api/device/1')
    if(r.status_code == 200):
        return r.json()
    else:
        return 

def getAddFaceData():
    r = requests.get('http://192.168.1.7/tarama/api/device/1/addface')
    if(r.status_code == 200):
        return r.json()
    else:
        return 

def setOnline():
    r = requests.post('http://192.168.1.7/tarama/api/device/1/online')
    if(r.status_code == 200):
        return r.json()
    else:
        return

def addFace(dataUser,pathImage):
    picture = "a"
    while True:
        # dapatkan frame, dan resize ke 500pixel agar lebih cepat
        frame = vs.read()
        frame = imutils.resize(frame, width=500)
        
                
        # Tampilkan gambar di layar
        cv2.imshow("Frame", frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        # update FPS
        fps.update()
        
        # tunggu tombol 1 untuk keluar
        if key == ord("q"):
            # tampilkan info FPS
            fps.stop()
            print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
            print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

            # cleanup
            cv2.destroyAllWindows()
            break
        elif key == ord(" "):
            cv2.imwrite(pathImage+"/"+dataUser["user"]["name"]+"_"+picture+".jpg", frame)
            print('[Info] Face Added')            
            i = ord(picture[0])
            i += 1
            picture = chr(i)
            if(i > 101):            
                # tampilkan info FPS
                fps.stop()
                print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
                print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

                # cleanup
                cv2.destroyAllWindows()
                
                # return Face
                returnAddFace()
                
                break
            
def returnAddFace(email):
    myobj = {'email': email,}
    r = requests.post('http://192.168.1.7/tarama/api/device/1/addface',data = myobj)
    if(r.status_code == 200):
        return r.json()
    else:
        return 
    
def scanFace():
    while True:
        # dapatkan frame, dan resize ke 500pixel agar lebih cepat
        frame = vs.read()
        frame = imutils.resize(frame, width=500)
        
        # Konversi ke grayscale dan konversi ke RGB
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # deteksi wajah dari frame grayscale
        rects = detector.detectMultiScale(gray, scaleFactor=1.1, 
            minNeighbors=5, minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE)

        # Tampilkan kotak di wajah yang dideteksi
        boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

        encodings = face_recognition.face_encodings(rgb, boxes)
        names = []

        # loop di semua wajah yang terdeteksi
        for encoding in encodings:
            matches = face_recognition.compare_faces(data["encodings"], encoding)
            name = "Unknown"

            # check apakah ada wajah yang di kenali
            if True in matches:
                print("Wajah Di Kenali")                
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}
                for i in matchedIdxs:
                    name = data["names"][i]
                    counts[name] = counts.get(name, 0) + 1
                name = max(counts, key=counts.get)
            names.append(name)
                

        # loop di semua wajah yang sudah di kenali
        for ((top, right, bottom, left), name) in zip(boxes, names):
            # tampilkan nama di wajah yang di kenali
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,0.75, (0, 255, 0), 2)

        # Tampilkan gambar di layar
        cv2.imshow("Frame", frame)
        
        key = cv2.waitKey(1) & 0xFF
        # tunggu tombol 1 untuk keluar
        if key == ord("q"):
            # tampilkan info FPS
            fps.stop()
            print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
            print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

            # cleanup
            cv2.destroyAllWindows()
            break
        
        # update FPS
        fps.update()

# loop dari semua frame yang di dapat
while True:
    if(checkInternetHttplib == False):        
        print("[INFO] Internet Tidak Terhubung")
        time.sleep(5)
        continue
    else:
        deviceData = getDevice()
        print("[INFO] Internet Terhubung")
        if(deviceData == None):
            print("[INFO] Server Offline")
        else:
            print("[INFO] Server Online")
            deviceOnline = setOnline()
            if(deviceData['is_scan'] != 0):                
                print('[INFO] Scanning')                
                scanFace()
            else:                
                if(deviceData['is_add_face'] != 0):   
                    print('[INFO] Add Face')
                    addFaceData = getAddFaceData()
                    if(addFaceData != None):
                        pathExist = path.exists("dataset/"+addFaceData["user"]["email"])
                        if(pathExist != True):
                            try:
                                os.makedirs("dataset/"+addFaceData["user"]["email"],access_rights)
                            except OSError:
                                print ("Creation of the directory /dataset/"+addFaceData["user"]["email"]+" failed")
                            else:
                                print ("Successfully created the directory /dataset/"+addFaceData["user"]["email"] )
                        addFace(addFaceData,"dataset/"+addFaceData["user"]["email"])
                else:
                    print('[INFO] Standby')          
    time.sleep(5)

# tampilkan info FPS
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# cleanup
cv2.destroyAllWindows()
vs.stop()

