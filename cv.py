from pathlib import Path
from ultralytics import YOLO


# ============================================================
# Paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

MODEL_PATH = (
    PROJECT_ROOT
    / "model_backup"
    / "carcare_yolo11n_seg_best.pt"
)


# ============================================================
# Load YOLO Model
# ============================================================

model = YOLO(str(MODEL_PATH))


# ============================================================
# Vehicle Part Detection
# ============================================================

def detect_vehicle_parts(
    image_path,
    conf=0.25
):
    results = model.predict(
        source=str(image_path),
        imgsz=640,
        conf=conf,
        device=0,
        verbose=False
    )

    result = results[0]

    detected_parts = []

    if result.boxes is None:
        return detected_parts

    for i in range(len(result.boxes)):

        class_id = int(
            result.boxes.cls[i].item()
        )

        confidence = float(
            result.boxes.conf[i].item()
        )

        class_name = result.names[class_id]

        detected_parts.append({
            "part": class_name,
            "confidence": round(
                confidence,
                4
            )
        })

    return detected_parts