import json
import sqlite3
from db.data_store import get_player, add_player, add_video, DuplicateVideoError
from db.db import init_db, get_connection
def migrate_to_sqlite(conn : sqlite3.Connection):
    with open("data.json") as json_file:
        loaded_data = json.load(json_file)
        for user, user_data  in loaded_data.items(): 
            #add player if not exist but if already exist just add data
            if get_player(user, conn) is None:
                add_player(user, user_data["gender"], conn)
            for day, videos in user_data["sessions"].items():
                for video_name, video_metrics in videos.items():
                    try:
                        add_video(user, video_name, day, video_metrics["peak_trunk_velocity"], video_metrics["peak_timing_ms_before_contact"], video_metrics["onset_ms_before_contact"], video_metrics["hip_shoulder_peak_diff_ms"], conn)
                    except DuplicateVideoError:
                        continue


def main():
    conn = get_connection()
    init_db(conn)
    migrate_to_sqlite(conn)

if __name__ == '__main__':
    main()