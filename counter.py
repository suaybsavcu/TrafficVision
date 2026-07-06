"""TrafficVision - Sanal çizgi geçiş sayacı."""


class LineCounter:
    def __init__(self, line_y: float):
        """line_y: sayım çizgisinin kare yüksekliğine oranı (0.0 - 1.0) yerine mutlak piksel y'si."""
        self.line_y = line_y
        self.counted_ids = set()
        self.last_position = {}  # object_id -> son y konumu
        self.count_by_class = {}

    def update(self, tracked_objects: dict) -> int:
        """tracked_objects: {object_id: {"centroid":(x,y), "class": str}}
        Döndürür: bu karede yeni sayılan araç sayısı
        """
        new_count = 0

        for object_id, data in tracked_objects.items():
            cy = data["centroid"][1]
            prev_y = self.last_position.get(object_id)

            if prev_y is not None and object_id not in self.counted_ids:
                # Çizgiyi yukarıdan aşağı ya da aşağıdan yukarı geçiş kontrolü
                crossed = (prev_y < self.line_y <= cy) or (prev_y > self.line_y >= cy)
                if crossed:
                    self.counted_ids.add(object_id)
                    cls = data.get("class", "vehicle")
                    self.count_by_class[cls] = self.count_by_class.get(cls, 0) + 1
                    new_count += 1

            self.last_position[object_id] = cy

        return new_count

    @property
    def total_count(self) -> int:
        return len(self.counted_ids)

    def summary(self) -> dict:
        return {"total": self.total_count, "by_class": dict(self.count_by_class)}
