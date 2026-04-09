from metric_extractor import MetricExtractor
from video_processor import VideoProcessor
import json
import sys
USER = "Logan"
VIDEO_PATH = "media/hit5 - Trim.mp4"
GENDER = "Male"
VIDEO_DATE = "01-17-2025"
try: 
    with open("data.json", "r") as json_file:
        loaded_data = json.load(json_file)
        if(USER not in loaded_data):
            loaded_data[USER] = {"sessions": []}
except FileNotFoundError:
    loaded_data = {}
    loaded_data[USER] = {"sessions": []}
user_data = loaded_data[USER]

try:
    video_processor = VideoProcessor(VIDEO_PATH, USER)
except FileNotFoundError as e:
    print(e)
    sys.exit(0)

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
        "date": VIDEO_DATE,
        "gender": GENDER,
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
        existing = user_data["sessions"]
        is_duplicate = False
        for i, s in enumerate(existing):
            if s["video"] == VIDEO_PATH and s["date"] == VIDEO_DATE:
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
            user_data["sessions"].append(session)



        with open("data.json", "w") as json_file:
            json.dump(loaded_data, json_file, indent=2)
else:
    print("You have to tag a contact frame with key c")




    