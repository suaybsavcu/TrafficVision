"""TrafficVision - Piksel hareketinden yaklaşık hız tahmini.

Not: Gerçek hız için kamera kalibrasyonu (piksel/metre oranı) gereklidir.
Burada basit bir "meters_per_pixel" varsayımıyla yaklaşık değer üretiriz.
"""
import time
from collections import deque


class SpeedEstimator:
    def __init__(self, meters_per_pixel: float = 0.05, history_len: int = 5):
        """
        meters_per_pixel: kameranın baktığı alanda 1 pikselin kaç metreye denk geldiği.
        Bu değer, gerçek dünyada bilinen bir referans mesafe (örn. şerit genişliği ~3.5m)
        ile kalibre edilmelidir.
        """
        self.meters_per_pixel = meters_per_pixel
        self.history_len = history_len
        self.track_history = {}  # object_id -> deque of (centroid, timestamp)

    def update(self, object_id, centroid):
        now = time.time()
        if object_id not in self.track_history:
            self.track_history[object_id] = deque(maxlen=self.history_len)
        self.track_history[object_id].append((centroid, now))

    def estimate_speed_kmh(self, object_id) -> float:
        history = self.track_history.get(object_id)
        if not history or len(history) < 2:
            return 0.0

        (x1, y1), t1 = history[0]
        (x2, y2), t2 = history[-1]

        dt = t2 - t1
        if dt <= 0:
            return 0.0

        pixel_dist = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        meters = pixel_dist * self.meters_per_pixel
        mps = meters / dt
        kmh = mps * 3.6
        return round(kmh, 1)

    def cleanup(self, active_ids):
        stale = [oid for oid in self.track_history if oid not in active_ids]
        for oid in stale:
            del self.track_history[oid]
