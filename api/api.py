from fastapi import FastAPI, Depends, HTTPException
from db.db import get_connection
from analysis.metric_analyzer import get_averages, get_trends
import sqlite3
import db.data_store as data_store
from exceptions.exceptions import MissingUserError, MissingVideoError

#read half of api endpoints (assume db already written to)

#raw history, single video metrics, and trends
app = FastAPI()
def get_db():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()



@app.get('/player_vids/{name}')
def get_player_hist(name, conn : sqlite3.Connection = Depends(get_db)):
    vids = data_store.get_all_videos(name, conn)
    if vids is None:
        raise HTTPException(status_code=404, detail="Player not found")
    else:
        return vids

@app.get('/player_vids/{name}/{vid_path:path}') #Nothing can come after vid path bc :path lets it take / in the text of vid path
def get_video(name, vid_path, conn : sqlite3.Connection = Depends(get_db)):
    vid_data = data_store.get_video(name, vid_path, conn)
    if vid_data is None:
        raise HTTPException(status_code=404, detail="Player or video not found")
    return dict(vid_data)

@app.get('/player/trends/{name}')
def get_metrics(name, conn : sqlite3.Connection = Depends(get_db)):
    try: 
        avg_peak_trunk_velo, avg_peak_timing_ms, avg_onset_ms, avg_hip_shoulder_peak_dif = get_averages(name, conn)
        trunk_velo_slope, peak_timing_trend, onset_timing_trend, hip_sep_trend = get_trends(name, conn)
    except MissingUserError:
        raise HTTPException(status_code=404, detail="Player not found")
    except MissingVideoError:
        #return -1 because no videos under this user
        return -1
    return (avg_peak_trunk_velo, avg_peak_timing_ms, avg_onset_ms, avg_hip_shoulder_peak_dif,
              trunk_velo_slope, peak_timing_trend, onset_timing_trend, hip_sep_trend)

    