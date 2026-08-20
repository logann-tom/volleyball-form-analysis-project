CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    name TEXT NOT NULL,
    gender TEXT NOT NULL CHECK (gender in ('Male', 'Female'))
);


CREATE TABLE IF NOT EXISTS videos(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    video_path TEXT NOT NULL, 
    date TEXT NOT NULL,
    peak_trunk_velocity FLOAT NOT NULL,
    peak_timing_ms_before_contact FLOAT NOT NULL,
    onset_ms_before_contact FLOAT, 
    hip_shoulder_peak_diff_ms FLOAT NOT NULL,
    unique(user_id, video_path)
);