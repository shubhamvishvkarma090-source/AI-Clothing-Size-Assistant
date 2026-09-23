import base64
import os
from pathlib import Path

import cv2
import numpy as np
from flask import Flask, jsonify, render_template, request

from calibration import calibrate
from cloth_detection import detect_cloth
from cloth_detection import get_bounding_box
from measurement import calculate_measurements
from measurement import summary_from_measurements


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

PROJECT_ROOT = Path(__file__).resolve().parent
RESULTS_DIR = PROJECT_ROOT / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

LATEST_MEASUREMENT = {
    "summary": "",
    "details": {},
    "image_path": "",
}


def save_result_image(image):
    image_path = RESULTS_DIR / "web_measurement.jpg"
    cv2.imwrite(str(image_path), image)
    return str(image_path)


def process_measurement(image):
    if image is None or image.size == 0:
        raise ValueError("No clothing image was received.")

    px_per_cm, marker_id = calibrate(
        image,
        5.0,
        fallback_pixels_per_cm=40.0,
    )

    contour, _ = detect_cloth(image)
    if contour is None:
        raise ValueError("No garment was detected. Try a clearer photo with good lighting.")

    _, _, width_pixels, height_pixels = get_bounding_box(contour)
    measurements = calculate_measurements(width_pixels, height_pixels, px_per_cm)
    summary = summary_from_measurements(measurements)

    output = image.copy()
    cv2.drawContours(output, [contour], -1, (0, 255, 0), 3)
    rotated_box = cv2.boxPoints(cv2.minAreaRect(contour))
    rotated_box = np.int32(rotated_box)
    cv2.drawContours(output, [rotated_box], 0, (255, 0, 0), 2)
    cv2.putText(output, f"Length: {measurements['length_cm']} cm", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(output, f"Chest: {measurements['chest_cm']} cm", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(output, f"Shoulder: {measurements['shoulder_cm']} cm", (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    image_path = save_result_image(output)
    LATEST_MEASUREMENT["summary"] = summary
    LATEST_MEASUREMENT["details"] = measurements
    LATEST_MEASUREMENT["image_path"] = image_path

    return {
        "marker_id": marker_id,
        "pixels_per_cm": round(px_per_cm, 2),
        "measurements": measurements,
        "summary": summary,
        "image_path": image_path,
    }


def decode_image_from_request():
    image_data = request.get_json(silent=True) or {}

    encoded = image_data.get("image")
    if encoded:
        if "," in encoded:
            _, encoded = encoded.split(",", 1)
        image_bytes = base64.b64decode(encoded)
        array = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(array, cv2.IMREAD_COLOR)
        return image

    uploaded = request.files.get("image")
    if uploaded is not None and uploaded.filename:
        file_bytes = uploaded.read()
        array = np.frombuffer(file_bytes, dtype=np.uint8)
        image = cv2.imdecode(array, cv2.IMREAD_COLOR)
        return image

    return None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/measure", methods=["POST"])
def measure_route():
    try:
        image = decode_image_from_request()
        if image is None:
            return jsonify({"ok": False, "error": "No image provided."}), 400

        result = process_measurement(image)
        return jsonify({"ok": True, "result": result})
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    except Exception as exc:  # pragma: no cover
        return jsonify({"ok": False, "error": f"Unexpected server error: {exc}"}), 500


@app.route("/chat", methods=["POST"])
def chat_route():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({"reply": "Please ask me about a garment measurement such as length, chest, shoulder, or waist."})

    text = message.lower()
    details = LATEST_MEASUREMENT.get("details") or {}
    if not details:
        return jsonify({"reply": "Please capture or upload a clothing photo first so I can measure it."})

    if any(keyword in text for keyword in ["summary", "overall", "size", "all"]):
        reply = LATEST_MEASUREMENT["summary"]
    elif "length" in text:
        reply = f"The garment length is {details.get('length_cm', 0):.2f} cm."
    elif "chest" in text:
        reply = f"The chest measurement is {details.get('chest_cm', 0):.2f} cm."
    elif "shoulder" in text:
        reply = f"The shoulder width is {details.get('shoulder_cm', 0):.2f} cm."
    elif "waist" in text:
        reply = f"The waist estimate is {details.get('waist_cm', 0):.2f} cm."
    elif "sleeve" in text:
        reply = f"The sleeve estimate is {details.get('sleeve_cm', 0):.2f} cm."
    else:
        reply = f"I can help with this garment. {LATEST_MEASUREMENT['summary']}"

    return jsonify({"reply": reply})


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "0").lower() in {"1", "true", "yes"}
    port = int(os.getenv("PORT", "5000"))
    app.run(debug=debug_mode, host="0.0.0.0", port=port)
