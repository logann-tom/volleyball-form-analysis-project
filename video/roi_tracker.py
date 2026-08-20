
class ROITracker:
    def __init__(self):
        self.center_history = []
        self.history_len = 5

    def update(self, frame_num, cx, cy):
        self.center_history.append((frame_num, cx, cy))
        if len(self.center_history) > self.history_len:
            self.center_history.pop(0)

    def get_velocity(self):
        if len(self.center_history) < 2:
            return 0.0, 0.0
        # average velocity over the window, not just last two frames
        (f0, x0, y0) = self.center_history[0]
        (f1, x1, y1) = self.center_history[-1]
        dt = f1 - f0
        if dt == 0:
            return 0.0, 0.0
        return (x1 - x0) / dt, (y1 - y0) / dt

    def predict_next(self):
        if not self.center_history:
            return None
        _, cx, cy = self.center_history[-1]
        vx, vy = self.get_velocity()
        return cx + vx, cy + vy