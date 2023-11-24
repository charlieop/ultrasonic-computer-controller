import numpy as np
import time


class AudioAnalyzer:
    def __init__(self, frequency, rate, chunk, radiusOfInterest):
        self.frequency = frequency
        self.chunk = chunk
        self.rate = rate
        self.radiusOfInterest = radiusOfInterest
        self.tragetIndex = int(frequency / rate * chunk)
        self.lastMovementTime = time.time()
        self.firstTapTime = time.time()
        
        self.detectedMovement = False
        
        self.left = False
        self.right = False
        self.left2 = False
        self.right2 = False
        
    def analyze(self, mag_data):
        rangeOfInterest = mag_data[self.tragetIndex - self.radiusOfInterest : self.tragetIndex + self.radiusOfInterest+1]
        if time.time() - self.lastMovementTime > 1:
            if self.detectedMovement:
                self.printOutput()
                self.detectedMovement = False
                self.left = False
                self.right = False
                self.left2 = False
                self.right2 = False
            elif self.detectMovement(mag_data, rangeOfInterest):
                print("movement detected", self.left, self.right)
        else:
            self.checkFollowUpMovement(mag_data, rangeOfInterest)
                
    
    def detectMovement(self, mag_data, rangeOfInterest):
        targetIndex = self.tragetIndex
        radiusOfInterest = self.radiusOfInterest
        if max(rangeOfInterest) < 5:
            print("speaker is off " + str(time.time()))
            return False
        
        # return if the frequency change is caused by noise (present in all frequency)
        noiseThreshold = 0.5
        if np.average(mag_data[targetIndex-40:targetIndex-10]) > noiseThreshold or np.average(mag_data[targetIndex+10:targetIndex+40]) > noiseThreshold:
            print("noise detected " + str(time.time()))
            return False
        
        # detect if there is a movement
        movementThreshold = 0.25
        if  np.average(rangeOfInterest[0: radiusOfInterest-3]) > movementThreshold:
            self.left = True
            self.detectedMovement = True
            self.lastMovementTime = time.time()
            return True
        if np.average(rangeOfInterest[radiusOfInterest+4: 2*radiusOfInterest+1] > movementThreshold):
            self.right = True
            self.detectedMovement = True
            self.lastMovementTime = time.time()
            return True
        
        return False
    
    def checkFollowUpMovement(self, mag_data, rangeOfInterest):
        # if not (self.left and self.right):
        #     movementThreshold = 0.20
        #     if self.left:
        #         if np.average(rangeOfInterest[self.radiusOfInterest+4: 2*self.radiusOfInterest+1] > movementThreshold):
        #             self.right = True
        #             self.firstTapTime = time.time()
        #     else:
        #         if np.average(rangeOfInterest[0: self.radiusOfInterest-3] > movementThreshold):
        #             self.left = True
        #             self.firstTapTime = time.time()
        if self.right and not self.left:   
            movementThreshold = 0.15
            if np.average(rangeOfInterest[0: self.radiusOfInterest-3] > movementThreshold):
                    self.left = True
                    self.firstTapTime = time.time()
                    
        elif self.right and self.left:
            movementThreshold = 0.15
            if np.average(rangeOfInterest[self.radiusOfInterest+4: 2*self.radiusOfInterest+1] > movementThreshold):
                    self.right2 = True
            if self.right2:
                if np.average(rangeOfInterest[0: self.radiusOfInterest-3] > movementThreshold):
                        self.left2 = True
                        
    def printOutput(self):
        if self.left and self.right and self.left2 and self.right2:
            print("double tap")
        elif self.left and self.right:
            print("single tap")
        elif self.left:
            print("up")
        elif self.right:
            print("down")
        print("\n============")
        
