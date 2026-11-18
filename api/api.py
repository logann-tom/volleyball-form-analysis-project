from fastapi import FastAPI, Depends, HTTPException
from db.db import get_connection
from analysis.metric_analyzer import get_averages, get_trends
import sqlite3
import db.data_store as data_store
from exceptions.exceptions import MissingUserError, MissingVideoError
from api.schemas import PlayerTrendsResponse, AverageMetrics, MetricTrends, Video, VideoList, BaseMetrics

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
#read half of api endpoints (assume db already written to)

#raw history, single video metrics, and trends
app = FastAPI()
def get_db():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()

def _row_to_vid(row : sqlite3.Row) -> Video:
    metrics = BaseMetrics(**row)
    return Video(metrics=metrics, **row)
@app.get('/player/{player_id}/videos')
def get_player_videos(player_id :int, conn : sqlite3.Connection = Depends(get_db)) -> Video:
    try:
        vids = data_store.get_all_videos_by_id(player_id, conn)
    except MissingUserError:
        raise HTTPException(status_code=404, detail="Player not found")
    res = []
    for vid in vids:
        res.append(_row_to_vid(vid))
    return VideoList(videos = res)
    
@app.get('/player/{player_id}/videos/{vid_id}') #Nothing can come after vid path bc :path lets it take / in the text of vid path
def get_video(player_id: int , vid_id : int, conn : sqlite3.Connection = Depends(get_db)) -> Video:
    try:
        vid_data = data_store.get_video_from_ids(player_id, vid_id, conn)
    except MissingUserError, MissingVideoError:
        raise HTTPException(status_code=404, detail="Player or video not found")
    return _row_to_vid(vid_data)

@app.get("/player/{player_id}/trends")
def get_player_trends(
    player_id: int, conn: sqlite3.Connection = Depends(get_db)
) -> PlayerTrendsResponse:
    try:
        averages = AverageMetrics(**get_averages(player_id, conn))
        try:
            trends = MetricTrends(**get_trends(player_id, conn))
        except MissingVideoError:
            trends = None
    except MissingUserError:
        raise HTTPException(status_code=404, detail="Player not found")
    except MissingVideoError:
        raise HTTPException(status_code=404, detail="Player has no videos to avg over")

    return PlayerTrendsResponse(averages=averages, trends=trends)
