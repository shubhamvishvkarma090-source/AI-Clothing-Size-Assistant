from pathlib import Path

import cv2

from calibration import calibrate
from cloth_detection import detect_cloth
from cloth_detection import get_bounding_box
from measurement import calculate_measurements
from measurement import summary_from_measurements


class GarmentChatbot:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index

    def capture_photo(self, output_path=None):
        camera = cv2.VideoCapture(self.camera_index)
        if not camera.isOpened():
            raise RuntimeError("Camera is not available. Please connect a camera or use an image file.")

        print("Camera ready. Position the garment in view and press SPACE to capture, ESC to quit.")
        captured = None

        while True:
            success, frame = camera.read()
            if not success:
                break

            cv2.imshow("Garment Measurement Assistant", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == 32:
                captured = frame.copy()
                break

            if key == 27:
                break

        cv2.destroyAllWindows()
        camera.release()

        if captured is None:
            raise RuntimeError("No image was captured from the camera.")

        if output_path is not None:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(output_path), captured)

        return captured

    def measure_image(self, image, pixel_scale=40.0, marker_size_cm=5.0, calibration_source=None):
        if image is None:
            raise ValueError("Image is empty.")

        calibration_image = calibration_source if calibration_source is not None else image
        px_per_cm, marker_id = calibrate(
            calibration_image,
            marker_size_cm,
            fallback_pixels_per_cm=pixel_scale,
        )

        contour, _ = detect_cloth(image)
        if contour is None:
            raise ValueError("Unable to detect the garment in the image.")

        _, _, width_pixels, height_pixels = get_bounding_box(contour)
        measurements = calculate_measurements(width_pixels, height_pixels, px_per_cm)
        summary = summary_from_measurements(measurements)

        return {
            "marker_id": marker_id,
            "pixels_per_cm": px_per_cm,
            "measurements": measurements,
            "summary": summary,
        }

    def run_capture_and_measure(self, output_dir=None, pixel_scale=40.0, marker_size_cm=5.0, show=False):
        output_dir = Path(output_dir) if output_dir is not None else Path("results")
        output_dir.mkdir(parents=True, exist_ok=True)

        image_path = output_dir / "captured_garment.jpg"
        image = self.capture_photo(output_path=image_path)
        result = self.measure_image(
            image,
            pixel_scale=pixel_scale,
            marker_size_cm=marker_size_cm,
            calibration_source=image,
        )

        if show:
            contour, edges = detect_cloth(image)
            if contour is not None:
                output = image.copy()
                cv2.drawContours(output, [contour], -1, (0, 255, 0), 3)
                cv2.putText(output, f"Length: {result['measurements']['length_cm']} cm", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(output, f"Chest: {result['measurements']['chest_cm']} cm", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.imshow("Garment Assistant Result", output)
                cv2.waitKey(0)
                cv2.destroyAllWindows()

        return result
