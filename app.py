import argparse
from pathlib import Path

import cv2
import numpy as np

from calibration import calibrate
from chatbot import GarmentChatbot
from cloth_detection import detect_cloth
from cloth_detection import get_bounding_box
from measurement import calculate_measurements
from measurement import summary_from_measurements


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_IMAGE = PROJECT_ROOT / "images" / "shirt.jpg"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "results"
DEFAULT_PIXELS_PER_CM = 40.0


def build_parser():
    parser = argparse.ArgumentParser(
        description="Measure garment dimensions from an image using ArUco calibration."
    )
    parser.add_argument(
        "--image",
        type=Path,
        default=DEFAULT_IMAGE,
        help="Path to the garment image to process."
    )
    parser.add_argument(
        "--calibration-image",
        type=Path,
        default=None,
        help="Optional path to a separate image that contains the ArUco marker for calibration."
    )
    parser.add_argument(
        "--marker-size-cm",
        type=float,
        default=5.0,
        help="Size of the ArUco marker in centimeters."
    )
    parser.add_argument(
        "--pixels-per-cm",
        type=float,
        default=DEFAULT_PIXELS_PER_CM,
        help="Manual calibration value to use when ArUco detection is unavailable."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Where to save annotated output images."
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Display the output image in a window."
    )
    parser.add_argument(
        "--camera",
        action="store_true",
        help="Use the camera to capture a garment image and measure it with the assistant."
    )
    parser.add_argument(
        "--chatbot",
        action="store_true",
        help="Start the interactive AI-style garment measurement assistant."
    )
    return parser


def _measure_from_image(image, calibration_source, marker_size_cm, pixels_per_cm, output_dir, show=False):
    try:
        px_per_cm, marker_id = calibrate(
            calibration_source,
            marker_size_cm,
            fallback_pixels_per_cm=pixels_per_cm
        )
    except ValueError as error:
        raise ValueError(f"Calibration Error: {error}") from error

    contour, edges = detect_cloth(image)
    if contour is None:
        raise ValueError("Cloth not detected.")

    _, _, w, h = get_bounding_box(contour)
    measurements = calculate_measurements(w, h, px_per_cm)

    output = image.copy()
    cv2.drawContours(output, [contour], -1, (0, 255, 0), 3)
    rotated_box = cv2.boxPoints(cv2.minAreaRect(contour))
    rotated_box = np.int32(rotated_box)
    cv2.drawContours(output, [rotated_box], 0, (255, 0, 0), 2)

    cv2.putText(output, f"Length: {measurements['length_cm']} cm", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(output, f"Chest: {measurements['chest_cm']} cm", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(output, f"Shoulder: {measurements['shoulder_cm']} cm", (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    measured_path = output_dir / "measured_cloth.jpg"
    edges_path = output_dir / "edges.jpg"
    cv2.imwrite(str(measured_path), output)
    cv2.imwrite(str(edges_path), edges)

    if show:
        cv2.imshow("Cloth Measurement", output)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return measurements, measured_path


def main(args=None):
    parser = build_parser()
    parsed_args = parser.parse_args(args)

    output_dir = parsed_args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if parsed_args.camera or parsed_args.chatbot:
        assistant = GarmentChatbot()
        try:
            result = assistant.run_capture_and_measure(
                output_dir=output_dir,
                pixel_scale=parsed_args.pixels_per_cm,
                marker_size_cm=parsed_args.marker_size_cm,
                show=parsed_args.show,
            )
        except KeyboardInterrupt:
            print("\nAssistant session ended.")
            return 0
        print("\nAI Assistant Summary:")
        print(result["summary"])
        return 0

    image_path = parsed_args.image.resolve()
    image = cv2.imread(str(image_path))

    if image is None:
        print(f"ERROR: Image not found: {image_path}")
        return 1

    print("\n================================")
    print(" CLOTH MEASUREMENT SYSTEM")
    print("================================")

    calibration_source = image
    if parsed_args.calibration_image is not None:
        calibration_source = cv2.imread(str(parsed_args.calibration_image.resolve()))
        if calibration_source is None:
            print(f"ERROR: Calibration image not found: {parsed_args.calibration_image}")
            return 1

    try:
        measurements, measured_path = _measure_from_image(
            image,
            calibration_source,
            parsed_args.marker_size_cm,
            parsed_args.pixels_per_cm,
            output_dir,
            show=parsed_args.show,
        )
    except ValueError as error:
        print(f"\n{error}")
        return 1

    print("\n--------------------------------")
    print("MEASUREMENT RESULT")
    print("--------------------------------")
    print(summary_from_measurements(measurements))
    print("--------------------------------")
    print("\nResult saved to:")
    print(measured_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())