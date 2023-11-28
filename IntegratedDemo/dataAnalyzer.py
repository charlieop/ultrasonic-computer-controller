import numpy as np
import time
from dirClassifier import DirClassifier
from computerController import Presets, ConputerController

class Gesture:
    def __init__(self):
        self.state = {
            "firstDown": False,
            "firstUp": False,
            "secondDown": False,
            "secondUp": False
            }
        self.lastMovedTime = time.time()
        self.controller = ConputerController(Presets.YOUTUBE)
    def reset(self):
        self.state = {
            "firstDown": False,
            "firstUp": False,
            "secondDown": False,
            "secondUp": False
            }
    def printResult(self):
        if self.state["firstDown"] and self.state["firstUp"] and self.state["secondDown"] and self.state["secondUp"]:
            print("double tap")
            self.makeAction("double tap")
        elif self.state["firstDown"] and self.state["firstUp"]:
            print("single tap")
            self.makeAction("single tap")
        elif self.state["firstDown"]:
            print("down")
            self.makeAction("down")
        elif self.state["firstUp"]:
            print("up")
            self.makeAction("up")
        print("\n==========")
    def makeAction(self, gesture):
        self.controller.makeAction(gesture)
        

class AudioAnalyzer:
    def __init__(self, frequency, rate, chunk, radiusOfInterest, otherFrequency = 0, useML = True):
        self.otherFrequency = otherFrequency
        self.targetIndexofOther = int(self.otherFrequency / rate * chunk)
        self.targetIndex = int(frequency / rate * chunk)
        self.frequency = frequency
        self.chunk = chunk
        self.rate = rate
        self.radiusOfInterest = radiusOfInterest
        self.useML = False
        self.useML = useML
        if useML:
            self.predictor = DirClassifier()
            self.label_thres = 0.08
            self.log = []

        self.gesture = Gesture()
        self.inDetection = False
        self.existMovement = False
        
        
    def analyze(self, mag_data):
        if self.useML:
            self.analyzeWithML(mag_data)
            return
        rangeOfInterest = mag_data[self.targetIndex - self.radiusOfInterest : self.targetIndex + self.radiusOfInterest+1]
        
        if self.inDetection:
            self.checkFollowUpMovement(rangeOfInterest)
            
        elif self.existMovement:
            self.gesture.printResult()
            self.gesture.reset()
            self.existMovement = False
            
        else:
            self.detectFirstMovement(mag_data, rangeOfInterest)
    
    def analyzeWithML(self, mag_data):
        
        rangeOfInterestMain = mag_data[self.targetIndex - self.radiusOfInterest : self.targetIndex + self.radiusOfInterest+1]
        rangeOfInterestOther = mag_data[self.targetIndexofOther - self.radiusOfInterest : self.targetIndexofOther + self.radiusOfInterest+1]
        if len(rangeOfInterestMain) < self.radiusOfInterest * 2 + 1 or len(rangeOfInterestOther) < self.radiusOfInterest * 2 + 1:
            print("not yet ready")
            return
        
        left_avg_Main = np.clip(np.average(rangeOfInterestMain[0: self.radiusOfInterest-2]), -0.5, 0.5)
        right_avg_Main = np.clip(np.average(rangeOfInterestMain[self.radiusOfInterest+3: -1]), -0.5, 0.5)
        left_avg_Other = np.clip(np.average(rangeOfInterestOther[0: self.radiusOfInterest-2]), -0.5, 0.5)
        right_avg_Other = np.clip(np.average(rangeOfInterestOther[self.radiusOfInterest+3: -1]), -0.5, 0.5)
        
        diffMain = (right_avg_Main - left_avg_Main)
        diffOther = (right_avg_Other - left_avg_Other)
        diff_Main_Other = (diffOther - diffMain)

        if (np.abs(diffMain) > self.label_thres) | (np.abs(diffOther) > self.label_thres) | (np.abs(diff_Main_Other) > self.label_thres):
            if not self.inDetection:
                print("==========movement========")
                self.inDetection = True
            res = self.predictor.get_class(diffOther, diffMain, diff_Main_Other)
            self.log.append(res[0])
            self.gesture.lastMovedTime = time.time()
        elif time.time() - self.gesture.lastMovedTime > 0.3 and self.inDetection:
            print("\n", self.log, "\n")
            down1 = False
            up1 = False
            down2 = False
            up2 = False
            down3 = False
            up3 = False
            for i in self.log:
                if i == "down":
                    down1 = True
                if down1 and i == "up":
                    up1 = True
                if up1 and i == "down":
                    down2 = True
                if down2 and i == "up":
                    up2 = True
                if up2 and i == "down":
                    down3 = True
                if down3 and i == "up":
                    up3 = True
                    
            if down1 and up1 and down2 and up2 and down3 and up3:
                print("triple tap")
                self.gesture.makeAction("triple tap")
            elif down1 and up1 and down2 and up2:
                print("double tap")
                self.gesture.makeAction("double tap")
            elif down1 and up1:
                print("single tap")
                self.gesture.makeAction("single tap")
            else:
                gest = max(self.log, key=self.log.count)
                print(gest)
                self.gesture.makeAction(gest)
                
            self.log = []
            self.inDetection = False   
    def detectFirstMovement(self, mag_data, rangeOfInterest):
        # if max(rangeOfInterest) < 1:
        #     print("speaker is off " + str(time.time()))
        #     return
        
        # return if the frequency change is caused by noise (present in all frequency)
        noiseThreshold = 0.5
        if (np.average(mag_data[self.targetIndex-40:self.targetIndex-10]) > noiseThreshold
        or np.average(mag_data[self.targetIndex+10:self.targetIndex+40]) > noiseThreshold):
            print("noise detected " + str(time.time()))
            return      
          
        # detect if there is a movement
        movementThreshold = 0.2
        if  np.average(rangeOfInterest[0: self.radiusOfInterest-3]) > movementThreshold:
            self.gesture.state["firstUp"] = True
            self.gesture.lastMovedTime = time.time()
            
            self.inDetection = True
            self.existMovement = True
            
        if np.average(rangeOfInterest[self.radiusOfInterest+4: 2*self.radiusOfInterest+1] > movementThreshold):
            self.gesture.state["firstDown"] = True
            self.gesture.lastMovedTime = time.time()

            self.inDetection = True
            self.existMovement = True
        if self.existMovement:
            print("movement detecting:")
        
    
    def checkFollowUpMovement(self, rangeOfInterest):
        # check if the movement endded
        if time.time() - self.gesture.lastMovedTime > 0.3:
            self.inDetection = False
            return
        
        # check if there is a second movement
        movementThreshold = 0.15
        up = np.average(rangeOfInterest[0: self.radiusOfInterest-3] > movementThreshold)
        down = np.average(rangeOfInterest[self.radiusOfInterest+4: 2*self.radiusOfInterest+1] > movementThreshold)
        
        if up or down:
            self.gesture.lastMovedTime = time.time()

        # check for single tap
        if self.gesture.state["firstDown"] and not self.gesture.state["firstUp"]: 
            self.gesture.state["firstUp"] = up
                    
        # check for double tap
        elif self.gesture.state["firstDown"] and self.gesture.state["firstUp"]:
            if down:
                self.gesture.state["secondDown"] = True
            if self.gesture.state["secondDown"] and up:
                    self.gesture.state["secondUp"] = True
        
