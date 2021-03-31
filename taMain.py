import requests
import time
import os
import os.path
from os import path
import json
try:
    import httplib
except:
    import http.client as httplib
import faceAdd 
 
# define the access rights
access_rights = 0o755

def checkEncodingsQueque():    
    pathExist = path.exists("encodingQueque.txt")
    if(pathExist):
        print("[Info] Check Encoding Queque")
        f = open("encodingQueque.txt", "r")
        jsonText = f.read()
        f.close()
        if(jsonText != " "):        
            print("[Info] Memulai Encoding")        
            jsonData = json.loads(jsonText)
            os.system("python3 face-encoding-user.py --dataset dataset/"+jsonData["user"]["email"]+" --encodings encodings/"+jsonData["user"]["email"]+".pickle --detection-method hog")
            with open('encodingQueque.txt', 'w') as f:
                f.write(' ')
        else:
            return False
    else:
        return False
        
    
def scanFace(email):
    os.system("python3 face-scan-video.py --cascade haarcascade_frontalface_default.xml  --encodings encodings/"+email+".pickle")

    print("[Info] Scan Face")
    return 

def addFace(dataUser,pathImage):
    data = {}
    user = {}
    user["id"] = dataUser["user"]["id"]
    user["name"] = dataUser["user"]["name"]
    user["email"] = dataUser["user"]["email"]
    data["user"] = user
    data["path"] = pathImage
    json_data = json.dumps(data)
    with open('addFace.txt', 'w') as outfile:
        json.dump(data, outfile)
    faceAdd.mainFunc()

def readAddedFace():
    while True:
        if(path.exists("addFaceDone.txt")):            
            print("[Info] Read Done File")
            f = open("addFaceDone.txt", "r")
            jsonText = f.read()
            f.close()
            if(jsonText != None):
                jsonData = json.loads(jsonText)
                if(jsonData["isDone"] == True):
                    returnAddFace(jsonData["user"]["email"])                   
                with open('addFaceDone.txt', 'w') as f:
                   f.write(' ')
                time.sleep(5)
                return True
            else:                
                print("[Info] Wait Add Face Finish")
                time.sleep(5)
        else:
            print("[Info] Wait Add Face Finish")
            time.sleep(5)
    
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
    r = requests.get('http://tarama.primexaviers.com/api/device/1')
    if(r.status_code == 200):
        return r.json()
    else:
        return 

def getAddFaceData():
    r = requests.get('http://tarama.primexaviers.com/api/device/1/addface')
    if(r.status_code == 200):
        return r.json()
    else:
        return 

def getScanFace():
    r = requests.get('http://tarama.primexaviers.com/api/device/1/scanFace')
    if(r.status_code == 200):
        return r.json()
    else:
        return

def setOnline():
    r = requests.post('http://tarama.primexaviers.com/api/device/1/online')
    if(r.status_code == 200):
        return r.json()
    else:
        return
    
def returnAddFace(userId):
    myobj = {'userId': userId,}
    r = requests.post('http://tarama.primexaviers.com/api/device/1/addFace/add',data = myobj)
    print(r.text)
    if(r.status_code == 200):
        return r.json()
    else:
        return 
    
def sendScanFace(userId,time):
    myobj = {'userId': userId,'time': time}
    r = requests.post('http://tarama.primexaviers.com/api/device/1/scan',data = myobj)
    if(r.status_code == 200):
        return r.json()
    else:
        return

# loop dari semua frame yang di dapat
while True:
    if(checkInternetHttplib == False):        
        print("[INFO] Internet Tidak Terhubung")
        time.sleep(5)
        continue
    else:
        encodingQueque = checkEncodingsQueque()
        if(encodingQueque != True):
            deviceData = getDevice()
            print("[INFO] Internet Terhubung")
            if(deviceData == None):
                print("[INFO] Server Offline")
            else:
                print("[INFO] Server Online")
                deviceOnline = setOnline()
                if(deviceData['is_scan'] != 0):
                    pathExist = path.exists("scanFaceDone.txt")
                    if(pathExist):
                        f = open("scanFaceDone.txt", "r")
                        jsonText = f.read()
                        f.close()
                        if(jsonText != " "):
                            dataScan = json.loads(jsonText)       
                            isSuccess = sendScanFace(dataScan["user"]["email"],dataScan["scanTime"]);                     
                            print("[Info] Send Scan to Database ")
                            if(isSuccess != None):                                                         
                                with open('scanFaceDone.txt', 'w') as f:
                                    f.write(' ')
                        else:
                            print('[INFO] Scanning')
                            dataScanFace = getScanFace()
                            if(dataScanFace != None):                        
                                scanFace(dataScanFace["user"]["email"])
                    else:
                        with open('scanFaceDone.txt', 'w') as f:
                            f.write(' ')
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
                            readAddedFace()
                    else:
                        print('[INFO] Standby')
        else:
            encodingImage()
            print('[INFO] Encoding Progress')
    time.sleep(5)
