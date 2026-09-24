import sqlite3
from exceptions.exceptions import MissingVideoError, DuplicateVideoError, MissingUserError
def get_player(name, conn : sqlite3.Connection):
    cursor = conn.cursor()
    player = cursor.execute('SELECT * FROM users WHERE name = ?', (name,)).fetchone()
    if(player is None):
        return None
    return player

def add_player(name, gender, conn : sqlite3.Connection):
    cursor = conn.cursor()
    gender = gender.lower()
    if(gender not in('male', 'female')):
        raise ValueError("Gender must be male or female")
    cursor.execute('INSERT into users (name, gender) VALUES (?, ?)', (name, gender))
    conn.commit()

def add_video(name, video_path, conn : sqlite3.Connection, date, trunk_velo, timing_before, onset, hip_sep, ):
    cursor = conn.cursor()
    if(get_video(name, video_path, conn) is not None):
        raise DuplicateVideoError("Video already exists")
    player = get_player(name, conn)
    if player is not None:
        player_id = player["id"]
    else:
        raise MissingUserError(f"User {name} does not exist")
    cursor.execute('INSERT into videos (user_id, video_path, date, peak_trunk_velocity, peak_timing_ms_before_contact, onset_ms_before_contact, hip_shoulder_peak_diff_ms) VALUES (?,?,?,?,?,?,?)',(player_id, video_path, date, trunk_velo, timing_before, onset, hip_sep))
    conn.commit()

def get_video(name, video_path, conn : sqlite3.Connection):
    cursor = conn.cursor()
    player = get_player(name, conn)
    if player is not None:
        player_id = player["id"]
    else:
        return None
    vid = cursor.execute('SELECT * from videos where user_id = ? AND video_path = ?', (player_id, video_path)).fetchone()
    if(vid is None):
        return None
    return vid

def get_all_videos(name, conn : sqlite3.Connection):
    cursor = conn.cursor()
    player = get_player(name, conn)
    if player is not None:
        player_id = player["id"]
    else:
        return None
    vids = cursor.execute('SELECT * FROM videos where user_id = ?', (player_id,)).fetchall()
    return vids


def update_video_date(name, video_path, conn : sqlite3.Connection, date):
    cursor = conn.cursor()
    vid = get_video(name, video_path, conn)
    if vid is None:
        raise MissingVideoError("Video does not exist")
    vid_id = vid["id"]
    cursor.execute('UPDATE videos SET date = ? WHERE id = ?', (date, vid_id))
    conn.commit()

def update_video_metrics(name,video_path, conn : sqlite3.Connection,trunk_velo , timing_before , onset , hip_sep ):
    cursor = conn.cursor()
    vid = get_video(name, video_path, conn)
    if vid is None:
        raise MissingVideoError("Video does not exist")
    vid_id = vid["id"]
    cursor.execute('UPDATE videos SET (peak_trunk_velocity, peak_timing_ms_before_contact, onset_ms_before_contact, hip_shoulder_peak_diff_ms) = (?,?,?,?) WHERE id = ?', (trunk_velo , timing_before , onset , hip_sep, vid_id,))
    conn.commit()
