#NOTE Vid length should be no longer than 20 seconds!
class PlayerData:
    MAX_SECONDS = 10
    def __init__(self, fps):
        self.frames = {}
        self.fps = fps
        self.max_shoulder_len = -100
        self.max_hip_len = -100
        

    def update(self, frame, landmarks):
        self.frames[frame] = landmarks
        #TODO Update max lengths for all values where that matters
    
    #Returns dictionary of frame and important metrics
    def getAllMetrics():
        #TODO calculate and return all important metrics to be tracked. 
        #Max length of shoulder/hip line is Hypotenuse (actual length)
        #observed length from 2D plane is adjacent
        #use arccos to get angle relative to camera

        
