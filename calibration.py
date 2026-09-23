from aruco_utils import detect_aruco_marker
from aruco_utils import pixels_per_cm


def calibrate(image, marker_size_cm=10.0, fallback_pixels_per_cm=None):
    if image is None:
        raise ValueError("Input image is empty.")

    if marker_size_cm <= 0:
        raise ValueError("Marker size must be greater than 0 cm.")

    try:
        corners, marker_id = detect_aruco_marker(image)
    except ValueError:
        if fallback_pixels_per_cm is not None:
            if fallback_pixels_per_cm <= 0:
                raise ValueError("Manual calibration value must be greater than 0.")
            return float(fallback_pixels_per_cm), None
        raise

    if corners is None:
        if fallback_pixels_per_cm is not None:
            if fallback_pixels_per_cm <= 0:
                raise ValueError("Manual calibration value must be greater than 0.")
            return float(fallback_pixels_per_cm), None

        raise ValueError(
            "ArUco marker not detected. "
            "Make sure the marker is clearly visible."
        )

    px_per_cm = pixels_per_cm(
        corners,
        marker_size_cm
    )

    if px_per_cm <= 0:
        raise ValueError("Detected marker scale is invalid.")

    return px_per_cm, marker_id