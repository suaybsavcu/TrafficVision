"""TrafficVision - Ana çalıştırma betiği.

Kullanım:
    python src/main.py --source videos/kavsak_ornek.mp4 --line-position 0.6
"""
import argparse
import sqlite3
import time
from pathlib import Path

import cv2

from detector import VehicleDetector
from tracker import CentroidTracker
from speed_estimator import SpeedEstimator
from counter import LineCounter

DB_PATH = "trafficvision.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS counts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            vehicle_class TEXT,
            speed_kmh REAL
        )
    """)
    conn.commit()
    return conn


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=str, default="0", help="Video dosyası ya da kamera index'i")
    parser.add_argument("--line-position", type=float, default=0.6, help="Sayım çizgisi (0-1 arası, kare yüksekliğine oran)")
    parser.add_argument("--meters-per-pixel", type=float, default=0.05)
    parser.add_argument("--show", action="store_true", help="Görüntüyü ekranda göster")
    args = parser.parse_args()

    source = int(args.source) if args.source.isdigit() else args.source
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise RuntimeError(f"Video kaynağı açılamadı: {args.source}")

    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    line_y = int(frame_height * args.line_position)

    detector = VehicleDetector()
    tracker = CentroidTracker()
    speed_estimator = SpeedEstimator(meters_per_pixel=args.meters_per_pixel)
    counter = LineCounter(line_y=line_y)

    conn = init_db()

    frame_idx = 0
    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        detections = detector.detect(frame)
        tracked = tracker.update(detections)

        for obj_id, data in tracked.items():
            speed_estimator.update(obj_id, data["centroid"])

        new_crossings = counter.update(tracked)

        if new_crossings > 0:
            for obj_id in list(counter.counted_ids)[-new_crossings:]:
                speed = speed_estimator.estimate_speed_kmh(obj_id)
                conn.execute(
                    "INSERT INTO counts (timestamp, vehicle_class, speed_kmh) VALUES (?, ?, ?)",
                    (time.time(), "vehicle", speed),
                )
            conn.commit()

        if args.show:
            cv2.line(frame, (0, line_y), (frame.shape[1], line_y), (0, 255, 0), 2)
            for obj_id, data in tracked.items():
                x1, y1, x2, y2 = map(int, data["bbox"])
                speed = speed_estimator.estimate_speed_kmh(obj_id)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(frame, f"ID{obj_id} {speed}km/h", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            cv2.putText(frame, f"Toplam: {counter.total_count}", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.imshow("TrafficVision", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        frame_idx += 1
        if frame_idx % 100 == 0:
            fps = frame_idx / (time.time() - start_time)
            print(f"Kare {frame_idx} - FPS: {fps:.1f} - Toplam sayım: {counter.summary()}")

    cap.release()
    cv2.destroyAllWindows()
    print("Bitti. Özet:", counter.summary())


if __name__ == "__main__":
    main()
