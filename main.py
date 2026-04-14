from metric_extractor import MetricExtractor
from video_processor import VideoProcessor
from metric_analyzer import analyze_sessions
import json
import datetime
USER = input("Enter your name: ")
new = False
#check if user is in data 
try: 
    with open("data.json", "r") as json_file:
        loaded_data = json.load(json_file)
        #if user not in data get gender
        if(USER not in loaded_data):
            new = True
            GENDER = input("Gender (Male/Female): ")
            while GENDER not in ["Male", "Female"]:
                GENDER = input("Gender must be Male or Female: ")
#if no saved data file yet create data to save later
except FileNotFoundError:
    loaded_data = {}
    new = True
    while GENDER not in ["Male", "Female"]:
        GENDER = input("Gender must be Male or Female: ")
if new:
    loaded_data[USER] = {"gender": GENDER, "sessions": []}
GENDER = loaded_data[USER]["gender"]
user_data = loaded_data[USER]
#get video path and date
valid_video = False
while not valid_video:
    VIDEO_PATH = input("Enter video path (full path or relative to project root): ")
    try:
        video_processor = VideoProcessor(VIDEO_PATH, USER)
        valid_video = True
    except FileNotFoundError as e:
        print(e)
valid_date = False
while not valid_date: 
    VIDEO_DATE = input("Enter video date (MM-DD-YYYY): ")
    try: 
        datetime.datetime.strptime(VIDEO_DATE, "%m-%d-%Y")
        valid_date = True
    except ValueError:
        valid_date = False


done = False
while not done:
    video_processor.process()
    print(video_processor.get_fps())
    #GRAPHING
    if(video_processor.get_contact_frame() != -1):

        extractor = MetricExtractor(video_processor.hitter, fps = video_processor.get_fps(), contact_frame= video_processor.get_contact_frame())
        extractor.graph_velocities()
        max_shoulder_velocity, peak_rotation_velocity_before_contact, shoulder_onset_before_contact, hip_shoulder_max_diff = extractor.get_metrics()

        #Store metrics to User
        session = {
            "video": VIDEO_PATH,
            "metrics": {
                "peak_trunk_velocity": max_shoulder_velocity,
                "peak_timing_ms_before_contact": peak_rotation_velocity_before_contact,
                "onset_ms_before_contact": shoulder_onset_before_contact,
                "hip_shoulder_peak_diff_ms": hip_shoulder_max_diff
            }
        }
        print("\nExtracted Metrics:")
        metrics = session["metrics"]
        print(f"  Peak trunk velocity: {metrics['peak_trunk_velocity']:.1f} °/s")
        print(f"  Peak timing before contact: {metrics['peak_timing_ms_before_contact']:.1f} ms")
        print(f"  Onset before contact: {metrics['onset_ms_before_contact']:.1f} ms")
        print(f"  Hip-shoulder peak diff: {metrics['hip_shoulder_peak_diff_ms']:.1f} ms")
        
        
        save = input("Save this session? (y/n)")
        if save.lower() == 'y':
            existing = user_data["sessions"][VIDEO_DATE]
            is_duplicate = False
            for i, s in enumerate(existing):
                if s["video"] == VIDEO_PATH:
                    is_duplicate = True
                    metrics = existing[i]["metrics"]
                    print("Video has already been processed, previous metrics: ")
                    print(f"  Peak trunk velocity: {metrics['peak_trunk_velocity']:.1f} °/s")
                    print(f"  Peak timing before contact: {metrics['peak_timing_ms_before_contact']:.1f} ms")
                    print(f"  Onset before contact: {metrics['onset_ms_before_contact']:.1f} ms")
                    print(f"  Hip-shoulder peak diff: {metrics['hip_shoulder_peak_diff_ms']:.1f} ms")
                    overwrite = input("\nOverwrite previous session? (y/n): ")
                    if overwrite.lower() == 'y':
                        existing[i] = session  # overwrite with new metrics
                    break

            if not is_duplicate:
                user_data["sessions"][VIDEO_DATE].append(session)


            with open("data.json", "w") as json_file:
                json.dump(loaded_data, json_file, indent=2)
        else: 
            redo = input("Redo? (y/n)")
            if redo.lower() == 'y':
                continue
        analyze = input(f"Analyze {USER}\'s sessions? (y/n)")
        if analyze.lower() == 'y':
            analyze_sessions(USER)
        done = True
    else:
        print("You have to tag a contact frame with key c")
        redo = input("Redo? (y/n)")
        if redo.lower() == 'y':
            done = False
        else: 
            done = True
            




    