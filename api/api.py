from fastapi import FastAPI, Depends, HTTPException
from db.db import get_connection
from analysis.metric_analyzer import get_averages, get_trends
import sqlite3
import db.data_store as data_store
from exceptions.exceptions import MissingUserError, MissingVideoError

"""
ALL ENDPOINTS:

get all player videos
player/{id}/videos

get a single video from player
player/{id}/videos/{vid_id} (should be updated to video id)

get trends
player/{id}/trends


Endpoints use ids over strings

"""
AVERAGE_KEYS = (
    "avg_peak_trunk_velo",
    "avg_peak_timing_ms",
    "avg_onset_ms",
    "avg_hip_shoulder_peak_dif",
)
TREND_KEYS = (
    "trunk_velo_slope",
    "peak_timing_trend",
    "onset_timing_trend",
    "hip_sep_trend",
)
#read half of api endpoints (assume db already written to)

#raw history, single video metrics, and trends
app = FastAPI()
def get_db():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()



@app.get('/player/{player_id}/videos')
def get_player_videos(player_id :int, conn : sqlite3.Connection = Depends(get_db)):
    vids = data_store.get_all_videos_by_id(player_id, conn)
    if vids is None:
        raise HTTPException(status_code=404, detail="Player not found")
    else:
        return vids
    
@app.get('/player/{player_id}/videos/{vid_id}') #Nothing can come after vid path bc :path lets it take / in the text of vid path
def get_video(player_id: int , vid_id : int, conn : sqlite3.Connection = Depends(get_db)):
    try:
        vid_data = data_store.get_video_from_ids(player_id, vid_id, conn)
    except MissingUserError, MissingVideoError:
        raise HTTPException(status_code=404, detail="Player or video not found")
    return dict(vid_data)

@app.get("/player/{player_id}/trends")
def get_metrics(player_id: int, conn: sqlite3.Connection = Depends(get_db)):
    try:
        averages = dict(zip(AVERAGE_KEYS, get_averages(player_id, conn), strict=True))
        try:
            trends = dict(zip(TREND_KEYS, get_trends(player_id, conn), strict=True))
        except MissingVideoError:
            trends = None
    except MissingUserError:
        raise HTTPException(status_code=404, detail="Player not found")

    return {"averages": averages, "trends": trends}

    