# import library yang di perlukan
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2
import os.path
from os import path
import json

if __name__ == '__main__':
    mainFunc()

def mainFunc():    
    if(path.exists("addFace.txt")):
        f = open("addFace.txt", "r")
        jsonData = json.loads(f.read())
        addFace(jsonData["user"],jsonData["path"])
        f.close()
        
        data = {}
        user = {}
        user["id"] = jsonData["user"]["id"]
        user["name"] = jsonData["user"]["name"]
        user["email"] = jsonData["user"]["email"]
        data["user"] = user
        data["path"] = jsonData["path"]
        data["isDone"] = True
        json_data = json.dumps(data)
        my_data_file = open('addFaceDone.txt', 'w')
        with open('addFaceDone.txt', 'w') as outfile:
            json.dump(data, outfile)
            
        with open('encodingQueque.txt', 'w') as outfile:
            json.dump(data, outfile)
            
        with open('addFace.txt', 'w') as f:
            f.write(' ')
        
        time.sleep(5)
            
    else:
        print("[Error] Add Face Failed")
    
def addFace(dataUser,pathImage):
    picture = "a"
    # Nyalakan Kamera
    print("[INFO] Memulai Stream dari Pi Camera...")
    vs = VideoStream(src=0).start()
    time.sleep(2.0)

    # Penghitung FPS (Frame per Second)
    fps = FPS().start()
    
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
            cv2.imwrite(pathImage+"/"+dataUser["name"]+"_"+picture+".jpg", frame)
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
                vs.stop()
                            
                break
            

            