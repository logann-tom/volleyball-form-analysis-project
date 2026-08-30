from video.metric_extractor import MetricExtractor
from video.video_processor import VideoProcessor
from analysis.metric_analyzer import analyze_sessions
from db.db import get_connection
from pathlib import Path
import json
import db.data_store as data_store
import datetime
def run():
    conn = get_connection()
    USER = input("Enter your name: ")
    new = data_store.get_player(USER, conn) is None
    #check if user is in data 
    if new:
        GENDER = input("Gender (Male/Female): ")
        while GENDER.lower() not in ["male", "female"]:
            GENDER = input("Gender must be Male or Female: ") 
        data_store.add_player(USER, GENDER, conn)
    
    #get video path
    valid_video = False
    while not valid_video:
        raw_path = input("Enter video path (full path or relative to project root): ")
        VIDEO_PATH = Path(raw_path).as_posix()
        try:
            video_processor = VideoProcessor(VIDEO_PATH, USER)
            valid_video = True
        except FileNotFoundError as e:
            print(e)
    #check if video exists under the user, if yes ask if date change is wanted, if no ask for date
    valid_date = False
    VIDEO_DATE = None
    date_change = False
    video = data_store.get_video(USER, VIDEO_PATH, conn)
    if video is not None:
        re_enter_date = input("This video is already tracked in a session, would you like to change its date? (y/n)")
        if re_enter_date.lower() == "n":
            valid_date = True
            VIDEO_DATE = video["date"]
        else:
            date_change = True
                 
    while not valid_date: 
        VIDEO_DATE = input("Enter video date (YYYY-MM-DD): ")
        try: 
            datetime.datetime.strptime(VIDEO_DATE, "%Y-%m-%d")
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
            new_metrics = {
                    "peak_trunk_velocity": max_shoulder_velocity,
                    "peak_timing_ms_before_contact": peak_rotation_velocity_before_contact,
                    "onset_ms_before_contact": shoulder_onset_before_contact,
                    "hip_shoulder_peak_diff_ms": hip_shoulder_max_diff
                }
            
            print("\nExtracted Metrics:")
            print(f"  Peak trunk velocity: {new_metrics['peak_trunk_velocity']:.1f} °/s")
            print(f"  Peak timing before contact: {new_metrics['peak_timing_ms_before_contact']:.1f} ms")
            print(f"  Onset before contact: {new_metrics['onset_ms_before_contact']:.1f} ms")
            print(f"  Hip-shoulder peak diff: {new_metrics['hip_shoulder_peak_diff_ms']:.1f} ms")
            
            
            save = input("Save this session? (y/n)")
            if save.lower() == 'y':
                is_duplicate = video is not None
                if is_duplicate:
                    print("Video has already been processed, previous metrics: ")
                    print(f"  Peak trunk velocity: {video['peak_trunk_velocity']:.1f} °/s")
                    print(f"  Peak timing before contact: {video['peak_timing_ms_before_contact']:.1f} ms")
                    print(f"  Onset before contact: {video['onset_ms_before_contact']:.1f} ms")
                    print(f"  Hip-shoulder peak diff: {video['hip_shoulder_peak_diff_ms']:.1f} ms")
                    overwrite = input("\nOverwrite previous session? (y/n): ")
                    if overwrite.lower() == 'y':
                        data_store.update_video_metrics(USER, VIDEO_PATH, conn, new_metrics['peak_trunk_velocity'], 
                                                        new_metrics['peak_timing_ms_before_contact'],
                                                        new_metrics['onset_ms_before_contact'],
                                                        new_metrics['hip_shoulder_peak_diff_ms']
                                                        ) # overwrite with new metrics
                        if date_change:
                            data_store.update_video_date(USER, VIDEO_PATH, conn, VIDEO_DATE)
                else:
                    data_store.add_video(USER, VIDEO_PATH, conn, VIDEO_DATE, new_metrics['peak_trunk_velocity'], 
                                                        new_metrics['peak_timing_ms_before_contact'],
                                                        new_metrics['onset_ms_before_contact'],
                                                        new_metrics['hip_shoulder_peak_diff_ms'],
                                                        )
            else:
                redo = input("Redo? (y/n)")
                if redo.lower() == 'y':
                    extractor.close_graph()
                    video_processor.reset()
                    continue
            extractor.close_graph()
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
                




if __name__ == '__main__':
    run()