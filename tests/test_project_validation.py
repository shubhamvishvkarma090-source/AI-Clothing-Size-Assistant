import unittest

import numpy as np

from aruco_utils import detect_aruco_marker
from calibration import calibrate
from cloth_detection import get_bounding_box
from measurement import calculate_measurements


class ProjectValidationTests(unittest.TestCase):
    def test_detect_aruco_marker_rejects_missing_image(self):
        with self.assertRaises(ValueError):
            detect_aruco_marker(None)

    def test_calculate_measurements_rejects_invalid_scale(self):
        with self.assertRaises(ValueError):
            calculate_measurements(200, 300, 0)

    def test_calibrate_uses_manual_fallback_when_marker_missing(self):
        image = __import__('cv2').imread('images/shirt.jpg')
        px_per_cm, marker_id = calibrate(image, 5.0, fallback_pixels_per_cm=40.0)
        self.assertEqual(px_per_cm, 40.0)
        self.assertIsNone(marker_id)

    def test_get_bounding_box_uses_rotated_contour_dimensions(self):
        contour = np.array([
            [[-14, -57]],
            [[57, 14]],
            [[14, 57]],
            [[-57, -14]],
        ], dtype=np.int32)

        x, y, w, h = get_bounding_box(contour)

        self.assertGreater(w, 0)
        self.assertGreater(h, 0)
        self.assertAlmostEqual(w, 100.0, delta=10.0)
        self.assertAlmostEqual(h, 60.0, delta=10.0)

    def test_calculate_measurements_includes_clothing_details(self):
        measurements = calculate_measurements(400, 600, 10.0)

        self.assertIn("length_cm", measurements)
        self.assertIn("chest_cm", measurements)
        self.assertIn("shoulder_cm", measurements)
        self.assertGreater(measurements["chest_cm"], measurements["shoulder_cm"])
        self.assertGreater(measurements["length_cm"], 0)

    def test_chatbot_summary_mentions_key_dimensions(self):
        measurements = {
            "length_cm": 70.0,
            "chest_cm": 102.0,
            "shoulder_cm": 42.0,
        }

        summary = __import__('measurement').summary_from_measurements(measurements)

        self.assertIn("Length", summary)
        self.assertIn("Chest", summary)
        self.assertIn("Shoulder", summary)


if __name__ == "__main__":
    unittest.main()
