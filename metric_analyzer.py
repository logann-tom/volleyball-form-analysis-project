import json 
import datetime
import numpy as np
import matplotlib.pyplot as plt

BENCHMARKS = {
    "Male": {
        'peak_trunk_velocity': 400,
        'onset_ms_before_contact': {"pro" : 220, "junior": 180}, #220 for pro, 180 for reg
        'peak_timing_ms_before_contact': {"pro": 60, "junior": 80} #peak velocity ms before contact pro 60ms before contact, teens 80ms

    },
    'Female': {
        'peak_trunk_velocity': 300,
        'onset_ms_before_contact': {"pro" : 220, "junior": 180}, #220 for pro, 180 for reg
        'peak_timing_ms_before_contact': {"pro": 50, "junior": 80} #peak velocity ms before contact pro 50ms before contact, teens 80ms
    }
}


def analyze_sessions(user):
    try: 
        with open("data.json", "r") as json_file:
            loaded_data = json.load(json_file)
            if(user not in loaded_data):
                print("The user has no sessions stored in data.json")
                return
            sessions = loaded_data[user]["sessions"]
            gender = loaded_data[user]["gender"]
            peak_trunk_velos = []
            peak_before_contacts = []
            onset_times = []
            hip_shoulder_sep_times = []
            #sort sessions by date
            sessions.sort(key = lambda s: datetime.datetime.strptime(s["date"],"%m-%d-%Y"))
            for session in sessions:
                #average values across day and append 
                date = session["date"]
                for video in session["videos"]:
                    metrics = video["metrics"]
                    peak_trunk_velos.append((date, metrics["peak_trunk_velocity"]))
                    peak_before_contacts.append((date, metrics["peak_timing_ms_before_contact"]))
                    onset_times.append((date, metrics["onset_ms_before_contact"]))
                    hip_shoulder_sep_times.append((date, metrics["hip_shoulder_peak_diff_ms"]))
            #output results
            output_results(peak_trunk_velos, peak_before_contacts, onset_times,hip_shoulder_sep_times, user, gender)
            
            
    except FileNotFoundError:
        print("please make sure you have a data.json in this directory")
def output_results(peak_trunk_velos, peak_before_contacts, onset_times,hip_shoulder_sep_times, user, gender):
            dates, peak_trunk_velos = zip(*peak_trunk_velos) if peak_trunk_velos else ([], [])
            dates, peak_before_contacts = zip(*peak_before_contacts) if peak_before_contacts else ([],[])
            dates, onset_times = zip(*onset_times) if onset_times else ([],[])
            dates, hip_shoulder_sep_times = zip(*hip_shoulder_sep_times) if hip_shoulder_sep_times else ([],[])

            #calc users averages
            num_vids = len(peak_trunk_velos)
            avg_peak_trunk_velo = sum(peak_trunk_velos) / num_vids
            avg_peak_timing_ms = sum(peak_before_contacts) / num_vids
            avg_onset_ms = sum(onset_times) / num_vids
            avg_hip_shoulder_peak_dif = sum(hip_shoulder_sep_times) / num_vids


            #get benchmarks
            benchmark_peak_trunk_velo = BENCHMARKS[gender]["peak_trunk_velocity"]
            benchmark_junior_peak_timing_ms = BENCHMARKS[gender]["peak_timing_ms_before_contact"]["junior"]
            benchmark_pro_peak_timing_ms = BENCHMARKS[gender]["peak_timing_ms_before_contact"]["pro"]
            benchmark_junior_onset_timing_ms = BENCHMARKS[gender]["onset_ms_before_contact"]["junior"]
            benchmark_pro_onset_timing_ms = BENCHMARKS[gender]["onset_ms_before_contact"]["pro"]
            #print
            print(f"==== Performance Analysis for {user} ====")
            print(f"Valid sessions analyzed: {num_vids}\n")

            print(f"  Peak Trunk Velocity:      {avg_peak_trunk_velo:.1f} °/s")
            print(f"  Benchmark: {benchmark_peak_trunk_velo} °/s")
            print(f"  {get_feedback(avg_peak_trunk_velo, benchmark_peak_trunk_velo, benchmark_peak_trunk_velo)}\n")

            print(f"  Peak Timing Before Contact: {avg_peak_timing_ms:.1f} ms")
            print(f"  Benchmarks — Junior: {benchmark_junior_peak_timing_ms} ms | Pro: {benchmark_pro_peak_timing_ms} ms")
            print(f"  {get_feedback(avg_peak_timing_ms, benchmark_junior_peak_timing_ms, benchmark_pro_peak_timing_ms, higher_is_better=False)}\n")

            print(f"  Onset Before Contact:     {avg_onset_ms:.1f} ms")
            print(f"  Benchmarks — Junior: {benchmark_junior_onset_timing_ms} ms | Pro: {benchmark_pro_onset_timing_ms} ms")
            print(f"  {get_feedback(avg_onset_ms, benchmark_junior_onset_timing_ms, benchmark_pro_onset_timing_ms, higher_is_better=False)}\n")


            print(f"  Hip Velocity Peak Before Shoulder {avg_hip_shoulder_peak_dif:.1f} ms")
            print("  (Hips should peak before shoulders — positive value indicates good kinetic chain sequencing)")

            #get users trends over time using linear regression
            date_objects = [datetime.datetime.strptime(d, "%m-%d-%Y") for d in dates]
            first_date = date_objects[0]
            days = [(d - first_date).days for d in date_objects]
            print(f"==== {user}\'s TRENDS =====")
            trunk_velo_slope, trunk_velo_intercept = np.polyfit(days, peak_trunk_velos, deg=1)
            print(f"  Trunk Velocity Trend: {trunk_velo_slope:+.1f} °/s per day")
            peak_timing_trend, peak_timing_intercept = np.polyfit(days, peak_before_contacts,deg=1)
            print(f"  Peak Velocity Before Contact Trend: {peak_timing_trend:+.1f} ms per day")
            onset_timing_trend, onset_timing_intercept  = np.polyfit(days, onset_times,deg=1)
            print(f"  Rotation Start Before Contact Trend: {onset_timing_trend:+.1f} ms per day")
            

            x_line = np.linspace(min(days), max(days), 100)

            fig, axes = plt.subplots(3, 1, figsize=(10, 10))

            axes[0].scatter(days, peak_trunk_velos, color='blue', label='Sessions')
            axes[0].plot(x_line, trunk_velo_slope * x_line + trunk_velo_intercept, color='red', label='Trend')
            axes[0].axhline(y=BENCHMARKS[gender]["peak_trunk_velocity"], color='green', linestyle='--', label='Benchmark')
            axes[0].set_ylabel('Peak Trunk Velocity (°/s)')
            axes[0].legend()

            axes[1].scatter(days, peak_before_contacts, color='blue', label='Sessions')
            axes[1].plot(x_line, peak_timing_trend * x_line + peak_timing_intercept, color='red', label='Trend')
            axes[1].axhline(y=BENCHMARKS[gender]["peak_timing_ms_before_contact"]["junior"], color='orange', linestyle='--', label='Junior benchmark')
            axes[1].axhline(y=BENCHMARKS[gender]["peak_timing_ms_before_contact"]["pro"], color='green', linestyle='--', label='Pro benchmark')
            axes[1].set_ylabel('Peak Timing (ms)')
            axes[1].legend()

            axes[2].scatter(days, onset_times, color='blue', label='Sessions')
            axes[2].plot(x_line, onset_timing_trend * x_line + onset_timing_intercept, color='red', label='Trend')
            axes[2].axhline(y=BENCHMARKS[gender]["onset_ms_before_contact"]["junior"], color='orange', linestyle='--', label='Junior benchmark')
            axes[2].axhline(y=BENCHMARKS[gender]["onset_ms_before_contact"]["pro"], color='green', linestyle='--', label='Pro benchmark')
            axes[2].set_ylabel('Onset (ms)')
            axes[2].set_xlabel('Days since first session')
            axes[2].legend()

            plt.tight_layout()
            plt.savefig("trends.png")
            plt.show()
            



def get_feedback(value, benchmark_junior, benchmark_pro, higher_is_better=True):
    if higher_is_better:
        if value >= benchmark_pro:
            return "✓ Exceeds pro benchmark"
        elif value >= benchmark_junior:
            return "~ At junior elite level"
        else:
            return f"✗ Below junior elite (target: {benchmark_junior})"
    else:  # lower is better (timing metrics)
        if value <= benchmark_pro:
            return "✓ Exceeds pro benchmark"
        elif value <= benchmark_junior:
            return "~ At junior elite level"
        else:
            return f"✗ Above junior elite target (aim for {benchmark_junior}ms)"


