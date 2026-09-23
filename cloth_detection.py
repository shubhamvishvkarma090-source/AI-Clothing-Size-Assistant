import cv2
import numpy as np


def detect_cloth(image, min_area=5000):
    if image is None:
        raise ValueError("Input image is empty.")

    if image.size == 0:
        raise ValueError("Input image is empty.")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)

    edges = cv2.Canny(blur, 50, 150)
    kernel = np.ones((5, 5), np.uint8)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(
        edges,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return None, edges

    filtered_contours = [
        contour for contour in contours
        if cv2.contourArea(contour) >= min_area
    ]

    if not filtered_contours:
        return None, edges

    cloth_contour = max(filtered_contours, key=cv2.contourArea)
    return cloth_contour, edges


def get_bounding_box(contour):
    if contour is None or len(contour) == 0:
        raise ValueError("Contour is empty.")

    rect = cv2.minAreaRect(contour)
    width, height = rect[1]
    long_side = max(width, height)
    short_side = min(width, height)

    cx, cy = rect[0]
    x = int(round(cx - long_side / 2.0))
    y = int(round(cy - short_side / 2.0))

    return x, y, long_side, short_side