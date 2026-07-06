"""TrafficVision - Basit merkez-nokta (centroid) tabanlı çoklu nesne takibi.

Not: Üretim ortamında ByteTrack/DeepSORT önerilir; bu, bağımlılık gerektirmeyen
hafif bir alternatiftir ve prototipleme için yeterlidir.
"""
import numpy as np


class CentroidTracker:
    def __init__(self, max_disappeared: int = 15, max_distance: float = 80.0):
        self.next_id = 0
        self.objects = {}         # id -> centroid
        self.disappeared = {}     # id -> kaç kare boyunca kayboldu
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance

    @staticmethod
    def _centroid(bbox):
        x1, y1, x2, y2 = bbox
        return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)

    def register(self, centroid):
        self.objects[self.next_id] = centroid
        self.disappeared[self.next_id] = 0
        self.next_id += 1

    def deregister(self, object_id):
        del self.objects[object_id]
        del self.disappeared[object_id]

    def update(self, detections):
        """detections: [{"bbox": (x1,y1,x2,y2), ...}, ...]
        Döndürür: {object_id: {"bbox":..., "centroid":...}}
        """
        input_centroids = [self._centroid(d["bbox"]) for d in detections]

        if len(input_centroids) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            return {}

        if len(self.objects) == 0:
            for c in input_centroids:
                self.register(c)
        else:
            object_ids = list(self.objects.keys())
            object_centroids = list(self.objects.values())

            D = np.linalg.norm(
                np.array(object_centroids)[:, np.newaxis] - np.array(input_centroids)[np.newaxis, :],
                axis=2,
            )

            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]

            used_rows, used_cols = set(), set()
            for row, col in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue
                if D[row, col] > self.max_distance:
                    continue
                object_id = object_ids[row]
                self.objects[object_id] = input_centroids[col]
                self.disappeared[object_id] = 0
                used_rows.add(row)
                used_cols.add(col)

            unused_rows = set(range(D.shape[0])) - used_rows
            for row in unused_rows:
                object_id = object_ids[row]
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)

            unused_cols = set(range(D.shape[1])) - used_cols
            for col in unused_cols:
                self.register(input_centroids[col])

        result = {}
        for i, (obj_id, centroid) in enumerate(self.objects.items()):
            det = min(detections, key=lambda d: np.linalg.norm(np.array(self._centroid(d["bbox"])) - np.array(centroid)))
            result[obj_id] = {"bbox": det["bbox"], "centroid": centroid, "class": det.get("class", "vehicle")}

        return result
