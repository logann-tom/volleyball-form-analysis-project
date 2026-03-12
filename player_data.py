import math
#NOTE Vid length should be no longer than 20 seconds!
class PlayerData:
    MAX_SECONDS = 10
    def __init__(self, fps):
        #frames so far stores landmarks, shoulder and hip lengths
        self.frames = {}
        self.fps = fps
        self.max_shoulder_len = -100
        self.max_hip_len = -100
    def _get_dist(self, p1, p2, crop_w, crop_h):
        dx = (p1.x - p2.x) * crop_w
        dy = (p1.y - p2.y) * crop_h
        return math.sqrt(dx**2 + dy**2)
    #TODO FIX WITH 3D as 2D GETS TOO INCONSISTENT DUE TO DISTANCE FROM CAMERA INCREASING
    def update(self, frame, landmarks, crop_w, crop_h):
        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]
        shoulder_len = self._get_dist(left_shoulder, right_shoulder, crop_w, crop_h)
        self.max_shoulder_len = max(self.max_shoulder_len, shoulder_len)
        left_hip = landmarks[23]
        right_hip = landmarks[24]
        hip_len = self._get_dist(left_hip, right_hip, crop_w, crop_h)
        self.max_hip_len = max(self.max_hip_len, hip_len)
        self.frames[frame] = [landmarks, shoulder_len, hip_len]


    def _get_rotation_angle(self,obs_len, max_len):
        return math.acos(obs_len/max_len)

    #Returns dictionary of frame and important metrics
    def getAllMetrics(self):
        print("PRINTING MAX LENGHTS")
        print("HIP: ", self.max_hip_len, "\nSHOULDER: ", self.max_shoulder_len)
        res = {}
        for frame, (landmark, shoulder_len, hip_len) in self.frames.items():
            #get shoulder angle
            shoulder_angle = self._get_rotation_angle(shoulder_len,self.max_shoulder_len)
            #get hip angle
            hip_angle = self._get_rotation_angle(hip_len,self.max_hip_len)
            res[frame] = [shoulder_angle, hip_angle]
        return res

        
