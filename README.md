# Volleyball Hitting Form Analysis

A computer vision tool for analyzing volleyball players' hitting biomechanics. It processes video recordings of volleyball hits and extracts quantitative performance metrics related to trunk rotation, hip rotation, and timing — helping coaches and athletes evaluate and improve hitting form.

---

## Features

- Pose skeleton tracking using MediaPipe's heavy 33-landmark model
- Interactive contact frame tagging for precise timing analysis
- Savitzky-Golay filtered velocity curves for shoulder and hip rotation
- Four key biomechanical metrics extracted per session
- Persistent JSON storage of sessions per user with duplicate prevention
- Velocity graph visualization with contact frame marker

---

## Metrics Extracted

| Metric | Description |
|---|---|
| **Peak Trunk Velocity** | Maximum shoulder rotation speed (°/s) |
| **Peak Timing Before Contact** | How many ms before contact the peak velocity occurs |
| **Shoulder Onset Before Contact** | When trunk rotation begins (ms before contact) |
| **Hip-Shoulder Peak Diff** | Time gap between hip and shoulder peak velocity (ms) |

Analysis is performed over a window of ±400ms before contact and ±80ms after contact.

---

## Setup

### Requirements

- Python 3.8+
- `pose_landmarker_heavy.task` — MediaPipe pose model (must be placed in the project root)

### Install dependencies

```bash
pip install opencv-python mediapipe numpy scipy matplotlib
```

---

## Usage

1. Set your configuration at the top of [main.py](main.py):

```python
USER = "YourName"
VIDEO_PATH = "media/your_video.mp4"
GENDER = "Male"   # or "Female"
VIDEO_DATE = "MM-DD-YYYY"
```

2. Run the script:

```bash
python main.py
```

3. **Draw a bounding box** around the hitter in the first frame and press enter.

4. The video plays with the pose skeleton overlaid. Use these controls:

| Key | Action |
|---|---|
| `p` | Pause / unpause |
| `.` | Step forward one frame (while paused) |
| `d` | Print current frame number to console |
| `c` | Tag current frame as the **contact frame** |
| `q` | Quit |

5. After tagging contact, metrics are computed and displayed. A velocity graph opens showing shoulder and hip rotation curves. Press `y` to save the session or `n` to discard.

6. After metrics are saved or discarded, there is an option to analyze the users trends. press  `y` to view the users trends and `n` to quit. 
---

## Project Structure

```
.
├── main.py                    # Entry point and pipeline orchestration
├── video_processor.py         # Frame-by-frame video processing and pose detection
├── player_data.py             # Pose landmark storage and angle calculations
├── metric_extractor.py        # Metric extraction and graph generation
├── metric_analyzer.py         # Reference benchmarks by gender
├── data.json                  # Persistent session storage
├── pose_landmarker_heavy.task # MediaPipe pose model
└── media/                     # Input video files
```

---

## Output

Sessions are saved to `data.json` with the following structure:

```json
{
  "Logan": {
    "gender": "Male",
    "sessions": [
      { "date": "01-17-2025",
        "videos": {
          "video": "media/hit2 - Trim.mp4",
            "metrics": {
              "peak_trunk_velocity": 465.24,
              "peak_timing_ms_before_contact": 165.19,
              "onset_ms_before_contact": 264.31,
              "hip_shoulder_peak_diff_ms": 0.0
            }
          }
      }
    ]
  }
}
```

The same video will not be stored twice.

---

## Reference Benchmarks

| Level | Gender | Peak Trunk Velocity |
|---|---|---|
| Elite | Male | ~400 °/s |
| Elite | Female | ~300 °/s |

---

## Notes

- Analysis is based on 2D video, so perspective and camera distance affect rotation angle accuracy. Normalize by keeping camera position consistent across sessions.
- The heavy MediaPipe model is used for best landmark accuracy. It is not included in the repository due to file size — download it from the [MediaPipe releases](https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker).
