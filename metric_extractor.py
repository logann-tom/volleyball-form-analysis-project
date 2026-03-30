from player_data import PlayerData
import numpy as np
import math
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt


ANALYSIS_WINDOW = [.4, .08]
class MetricExtractor:
    def __init__(self, hitter : PlayerData, fps, contact_frame):
        self.hitter = hitter
        self.fps = fps
        frame_to_shoulder_hip_angles = hitter.getAllMetrics()
        angles = np.array(list(frame_to_shoulder_hip_angles.values()))
        self.frames = list(frame_to_shoulder_hip_angles.keys())
        shoulder_angles = angles[:,0]
        hip_angles = angles[:,1]
        shoulder_smooth = savgol_filter(shoulder_angles, window_length=9, polyorder=2)
        hip_smooth = savgol_filter(hip_angles, window_length=9, polyorder=2)
        shoulder_velocities = np.gradient(shoulder_smooth, 1/fps) 
        hip_velocities = np.gradient(hip_smooth, 1/fps)
        self.shoulder_velocities_deg = shoulder_velocities * -1 * 180 / np.pi
        self.hip_velocities_deg = hip_velocities * -1 * 180 / np.pi
        self.contact_frame = contact_frame

        self.window_start = math.floor(contact_frame - ANALYSIS_WINDOW[0] * fps)
        self.window_end = math.ceil(contact_frame + ANALYSIS_WINDOW[1] * fps)

    def graph_velocities(self):

        plot_start = self.window_start
        plot_end = self.window_end

        plt.figure()
        plt.plot(self.frames[plot_start:plot_end],self.shoulder_velocities_deg[plot_start:plot_end], label="Shoulder Velocity", color="red")
        plt.plot(self.frames[plot_start:plot_end], self.hip_velocities_deg[plot_start:plot_end], label="Hip Velocity", color="blue")
        plt.axvline(self.contact_frame)
        plt.xlabel("frames")
        plt.legend()
        plt.show()

        
    def get_onset_frame(self, velocities, min_consecutive=3):
        for i in range(len(velocities)):
            if all(velocities[i:i+min_consecutive] > 0):
                return i
        return None


    #CONTACT FRAME SHLD BE REALTIVE TO START OF VELOCITIES ARRAY
    def get_metrics(self):
        windowed_shoulder = self.shoulder_velocities_deg[self.window_start:self.window_end]
        windowed_hip = self.hip_velocities_deg[self.window_start:self.window_end]
        contact_frame = self.contact_frame - self.window_start
        max_shoulder_velocity_frame = np.argmax(windowed_shoulder) 
        max_shoulder_velocity = windowed_shoulder[max_shoulder_velocity_frame]

        max_hip_velocity_frame = np.argmax(windowed_hip)

        delta_shoulder = contact_frame - max_shoulder_velocity_frame
        #in MS
        peak_rotation_velocity_before_contact = delta_shoulder / self.fps * 1000
        
        #get when trunk(shoulder starts rotating)
        shoulder_onset_frame = self.get_onset_frame(windowed_shoulder)
        if shoulder_onset_frame is None:
            shoulder_onset_before_contact = None
        else: 
            shoulder_onset_before_contact = (contact_frame - shoulder_onset_frame) / self.fps * 1000

        #get difference in hip -> shoulder max velocity
        hip_shoulder_max_diff = (max_shoulder_velocity_frame - max_hip_velocity_frame) / self.fps * 1000

        return max_shoulder_velocity, peak_rotation_velocity_before_contact, shoulder_onset_before_contact, hip_shoulder_max_diff
