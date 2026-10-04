from pydantic import BaseModel

class BaseMetrics(BaseModel):
    peak_trunk_velocity : float
    peak_timing_ms_before_contact : float
    onset_ms_before_contact : float
    hip_shoulder_peak_diff_ms : float

class AverageMetrics(BaseModel):
    avg_peak_trunk_velocity : float
    avg_peak_timing_ms_before_contact : float
    avg_onset_ms_before_contact : float
    avg_hip_shoulder_peak_diff_ms : float

class MetricTrends(BaseModel):
    trunk_velo_slope : float
    peak_timing_trend : float
    onset_timing_trend : float
    hip_sep_trend : float

class Video(BaseModel):
    id: int
    user_id : int
    video_path : str
    date : str
    metrics : BaseMetrics


class VideoList(BaseModel):
    videos : list[Video]

class PlayerTrends(BaseModel):
    averages : AverageMetrics
    trends : MetricTrends