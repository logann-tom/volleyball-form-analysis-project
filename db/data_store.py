import sqlite3
import datetime
from exceptions.exceptions import MissingVideoError, DuplicateVideoError, MissingUserError

"""
Methods needed:

GETTERS:
Get player (by name, by id) name for terminal, id for api
Get ids (from player name) name getter wraps id getters

get single video (by player_id and vid_id, by name and vid path)
get all videos (by name and player_id)

ADDING: 
add player(name gender)
add video (name (prob also id), vid path, all 4 metrics)

UPDATING:
update vid date
update vid metrics

HELPERS:
_get_player_id (gets players id from name) 
_get_player_by_id (gets player object from id)

"""
#region Getters
#get by name looks for id by name and returns none if no exist, 
#get by id means we are assuming id exists so throws exception if no exist

def get_player(name : str, conn : sqlite3.Connection):
    cursor = conn.cursor()
    player = cursor.execute('SELECT * FROM users WHERE name = ?', (name,)).fetchone()
    if(player is None):
        return None
    return player

def _get_player_id(name : str, conn : sqlite3.Connection):
    player = get_player(name,conn)
    if(player is None):
        return None
    return player['id']

def _get_player_by_id(id :int, conn :sqlite3.Connection):
    cursor = conn.cursor()
    player = cursor.execute('SELECT 1 FROM users WHERE id = ?)', (id,)).fetchone()
    if(player is None):
        return None
    return player

def get_video(name : str, video_path : str, conn : sqlite3.Connection):
    id = _get_player_id(name, conn)
    if(id is None):
        return None
    else:
        try:
            return get_video_from_id(id, video_path, conn)
        except MissingVideoError, MissingUserError: 
            return None

def get_video_from_id(player_id :int, video_path : str, conn : sqlite3.Connection):
    if(_get_player_by_id(player_id, conn) is None):
        raise MissingUserError("This player id does not exist")
    cursor = conn.cursor()
    vid = cursor.execute('SELECT * from videos where user_id = ? AND video_path = ?', (player_id, video_path)).fetchone()
    if(vid is None):
        raise MissingVideoError("video you are trying to get is not owned by player or doesnt exist")
    return vid

def get_video_from_ids(player_id :int, video_id :int, conn : sqlite3.Connection):
    if(_get_player_by_id(player_id, conn) is None):
        raise MissingUserError("This player id does not exist")
    cursor = conn.cursor()
    vid = cursor.execute("SELECT 1 from videos WHERE user_id = ? AND id = ?", (player_id, video_id)).fetchone()
    if(vid is None):
        raise MissingVideoError("video you are trying to get is not owned by player or doesnt exist")
    return vid


def get_all_videos(name :str, conn : sqlite3.Connection):
    id = _get_player_id(name, conn)
    if id is None:
        return None
    else:
        return get_all_videos_by_id(id, conn)

def get_all_videos_by_id(id :int, conn : sqlite3.Connection):
    cursor = conn.cursor()
    vids = cursor.execute('SELECT * FROM videos where user_id = ?', (id,)).fetchall()
    return vids

#endregion 
#region Setters
def update_video_date(name:str, video_path :str, conn : sqlite3.Connection, date : str):
    try:
        datetime.datetime.strptime(date, "%Y-%m-%d")
    except ValueError: 
        raise ValueError("Date format must be in YYYY-MM-DD")
    cursor = conn.cursor()
    vid = get_video(name, video_path, conn)
    if vid is None:
        raise MissingVideoError("Video does not exist")
    vid_id = vid["id"]
    cursor.execute('UPDATE videos SET date = ? WHERE id = ?', (date, vid_id))
    conn.commit()

def update_video_metrics(name,video_path, conn : sqlite3.Connection, trunk_velo , timing_before , onset , hip_sep ):
    cursor = conn.cursor()
    vid = get_video(name, video_path, conn)
    if vid is None:
        raise MissingVideoError("Video does not exist")
    vid_id = vid["id"]
    cursor.execute('UPDATE videos SET (peak_trunk_velocity, peak_timing_ms_before_contact, onset_ms_before_contact, hip_shoulder_peak_diff_ms) = (?,?,?,?) WHERE id = ?', (trunk_velo , timing_before , onset , hip_sep, vid_id,))
    conn.commit()


def add_player(name :str, gender :str, conn : sqlite3.Connection):
    cursor = conn.cursor()
    gender = gender.lower()
    if(gender not in('male', 'female')):
        raise ValueError("Gender must be male or female")
    cursor.execute('INSERT into users (name, gender) VALUES (?, ?)', (name, gender))
    conn.commit()

def add_video(name :str , video_path:str, conn : sqlite3.Connection, date, trunk_velo, timing_before, onset, hip_sep):
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
#endregion