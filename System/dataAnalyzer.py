import numpy as np
import time

class Gesture:
    def __init__(self):
        self.state = {
            "firstDown": False,
            "firstUp": False,
            "secondDown": False,
            "secondUp": False
            }
        self.lastMovedTime = time.time()
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
        elif self.state["firstDown"] and self.state["firstUp"]:
            print("single tap")
        elif self.state["firstDown"]:
            print("down")
        elif self.state["firstUp"]:
            print("up")
        print("\n==========")
        

class AudioAnalyzer:
    def __init__(self, frequency, rate, chunk, radiusOfInterest):
        self.frequency = frequency
        self.chunk = chunk
        self.rate = rate
        self.radiusOfInterest = radiusOfInterest
        self.targetIndex = int(frequency / rate * chunk)

        self.gesture = Gesture()
        self.inDetection = False
        self.existMovement = False

        
    def analyze(self, mag_data):
        rangeOfInterest = mag_data[self.targetIndex - self.radiusOfInterest : self.targetIndex + self.radiusOfInterest+1]
        
        
        
        if self.inDetection:
            self.checkFollowUpMovement(rangeOfInterest)
            
        elif self.existMovement:
            self.gesture.printResult()
            self.gesture.reset()
            self.existMovement = False
            
        else:
            self.detectFirstMovement(mag_data, rangeOfInterest)
            
                
    
    def detectFirstMovement(self, mag_data, rangeOfInterest):
        if max(rangeOfInterest) < 5:
            print("speaker is off " + str(time.time()))
            return
        
        # return if the frequency change is caused by noise (present in all frequency)
        noiseThreshold = 0.5
        if (np.average(mag_data[self.targetIndex-40:self.targetIndex-10]) > noiseThreshold
        or np.average(mag_data[self.targetIndex+10:self.targetIndex+40]) > noiseThreshold):
            print("noise detected " + str(time.time()))
            return      
          
        # detect if there is a movement
        movementThreshold = 0.25
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
        
