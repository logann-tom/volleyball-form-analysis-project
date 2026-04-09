import json 
BENCHMARKS = {
    "male": {
        'peak_trunk_velocity': 400,
        'onset_ms_before_contact': {"pro" : 220, "junior": 180}, #220 for pro, 180 for reg
        'peak_timing_ms_before_contact': {"pro": 60, "junior": 80} #peak velocity ms before contact pro 60ms before contact, teens 80ms

    },
    'female': {
        'peak_trunk_velocity': 300,
        'onset_ms_before_contact': {"pro" : 220, "junior": 180}, #220 for pro, 180 for reg
        'peak_timing_ms_before_contact': {"pro": 50, "junior": 80} #peak velocity ms before contact pro 50ms before contact, teens 80ms
    }
}
USER = "Logan"
try: 
    with open("data.json", "r") as json_file:
        loaded_data = json.load(json_file)
        if(USER not in loaded_data):
            loaded_data[USER] = {"sessions": []}

        
except FileNotFoundError:
    print("this user does not exist")

def analyze_sessions(user):
    try: 
        with open("data.json", "r") as json_file:
            loaded_data = json.load(json_file)
            if(user not in loaded_data):
                print("The user has no sessions stored in data.json")
                return
            sessions = loaded_data[user]
            peak_trunk_velos = []
            peak_before_contacts = []
            onset_times = []
            hip_shoulder_sep_times = []
            for session in sessions:
                metrics = session["metrics"]
                peak_trunk_velos.append(metrics["peak_trunk_velocity"])
                peak_before_contacts.append(metrics["peak_timing_ms_before_contact"])
                onset_times.append(metrics["onset_ms_before_contact"])
                hip_shoulder_sep_times.append(metrics["hip_shoulder_peak_diff_ms"])

            avg_peak_trunk_velo = sum(peak_trunk_velos) / len(sessions)
            avg_peak_timing_ms = sum(peak_before_contacts) / len(sessions)
            avg_onset_ms = sum(onset_times) / len(sessions)
            avg_hip_shoulder_peak_dif = sum(hip_shoulder_sep_times) / len(sessions)




            
    except FileNotFoundError:
        print("please make sure you have a data.json in this directory")