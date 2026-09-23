import cv2
import numpy as np


ARUCO_DICTIONARY = cv2.aruco.getPredefinedDictionary(
    cv2.aruco.DICT_4X4_50
)


def detect_aruco_marker(image):
    if image is None:
        raise ValueError("Input image is empty.")

    if not isinstance(image, np.ndarray):
        raise ValueError("Input image must be a NumPy array.")

    if image.size == 0 or image.ndim < 2:
        raise ValueError("Input image is empty.")

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    parameters = cv2.aruco.DetectorParameters()

    parameters.adaptiveThreshWinSizeMin = 3
    parameters.adaptiveThreshWinSizeMax = 23
    parameters.adaptiveThreshWinSizeStep = 4
    parameters.minMarkerPerimeterRate = 0.02
    parameters.maxMarkerPerimeterRate = 4.0

    detector = cv2.aruco.ArucoDetector(
        ARUCO_DICTIONARY,
        parameters
    )

    corners, ids, rejected = detector.detectMarkers(gray)

    if ids is None or len(ids) == 0:
        return None, None

    return corners[0], int(ids[0][0])


def marker_pixel_size(corners):
    if corners is None:
        raise ValueError("Marker corners are missing.")

    points = corners.reshape(4, 2)
    sides = []

    for i in range(4):
        p1 = points[i]
        p2 = points[(i + 1) % 4]
        distance = np.linalg.norm(p1 - p2)
        sides.append(distance)

    return sum(sides) / len(sides)


def pixels_per_cm(corners, marker_size_cm):
    if marker_size_cm <= 0:
        raise ValueError("Marker size must be greater than 0 cm.")

    pixel_size = marker_pixel_size(corners)
    return pixel_size / marker_size_cm