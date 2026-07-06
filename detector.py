"""TrafficVision - YOLOv8 tabanlı araç tespiti."""
from ultralytics import YOLO

# COCO sınıflarında araçlarla ilgili id'ler
VEHICLE_CLASSES = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}


class VehicleDetector:
    def __init__(self, model_path: str = "yolov8n.pt", conf: float = 0.4):
        self.model = YOLO(model_path)
        self.conf = conf

    def detect(self, frame):
        """Tek bir kare üzerinde araç tespiti yapar.

        Döndürür: [{"bbox": (x1,y1,x2,y2), "class": str, "conf": float}, ...]
        """
        results = self.model.predict(frame, conf=self.conf, classes=list(VEHICLE_CLASSES.keys()), verbose=False)
        detections = []

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                x1, y1, x2, y2 = map(float, box.xyxy[0])
                detections.append({
                    "bbox": (x1, y1, x2, y2),
                    "class": VEHICLE_CLASSES.get(cls_id, "unknown"),
                    "conf": conf,
                })

        return detections


if __name__ == "__main__":
    import sys
    import cv2

    detector = VehicleDetector()
    cap = cv2.VideoCapture(sys.argv[1] if len(sys.argv) > 1 else 0)
    ret, frame = cap.read()
    if ret:
        detections = detector.detect(frame)
        print(f"{len(detections)} araç tespit edildi:")
        for d in detections:
            print(f"  {d['class']} (conf={d['conf']:.2f}) @ {d['bbox']}")
    cap.release()
