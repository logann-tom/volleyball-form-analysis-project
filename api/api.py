from fastapi import FastAPI, Depends, HTTPException
from db.db import get_connection
from analysis.metric_analyzer import get_averages, get_trends
import sqlite3
import db.data_store as data_store
from exceptions.exceptions import MissingUserError, MissingVideoError

"""
ALL ENDPOINTS:

get all player videos
player/id/videos

get a single video from player
player/id/videos/path (should be updated to video id)

get trends
player/id/trends


Endpoints use ids over strings

"""
#read half of api endpoints (assume db already written to)

#raw history, single video metrics, and trends
app = FastAPI()
def get_db():
    conn = get_connection()
    print("HI")
    try:
        yield conn
    finally:
        print("HI")
        conn.close()



@app.get('player/{player_id}/videos')
def get_player_videos(player_id :int, conn : sqlite3.Connection = Depends(get_db)):
    print("HI")
    vids = data_store.get_all_videos_by_id(player_id)
    if vids is None:
        raise HTTPException(status_code=404, detail="Player not found")
    else:
        return vids
    
@app.get('/player/{player_id}/videos/{vid_id}') #Nothing can come after vid path bc :path lets it take / in the text of vid path
def get_video(player_id, vid_id, conn : sqlite3.Connection = Depends(get_db)):
    try:
        vid_data = data_store.get_video_from_ids(player_id, vid_id, conn)
    except MissingUserError, MissingVideoError:
        raise HTTPException(status_code=404, detail="Player or video not found")
    return dict(vid_data)

@app.get('/player/{player_id}/trends')
def get_metrics(player_id, conn : sqlite3.Connection = Depends(get_db)):
    try: 
        avg_peak_trunk_velo, avg_peak_timing_ms, avg_onset_ms, avg_hip_shoulder_peak_dif = get_averages(player_id, conn)
        trunk_velo_slope, peak_timing_trend, onset_timing_trend, hip_sep_trend = get_trends(player_id, conn)
    except MissingUserError:
        raise HTTPException(status_code=404, detail="Player not found")
    except MissingVideoError:
        #return -1 because no videos under this user
        return -1
    return (avg_peak_trunk_velo, avg_peak_timing_ms, avg_onset_ms, avg_hip_shoulder_peak_dif,
              trunk_velo_slope, peak_timing_trend, onset_timing_trend, hip_sep_trend)

    