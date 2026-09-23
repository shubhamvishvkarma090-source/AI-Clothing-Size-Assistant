def pixel_to_cm(pixel_value, pixels_per_cm):
    if pixels_per_cm <= 0:
        raise ValueError("Invalid calibration value.")

    if pixel_value < 0:
        raise ValueError("Pixel measurements cannot be negative.")

    return pixel_value / pixels_per_cm


def calculate_measurements(
    width_pixels,
    height_pixels,
    pixels_per_cm
):
    if width_pixels <= 0 or height_pixels <= 0:
        raise ValueError("Width and height must be positive values.")

    width_cm = pixel_to_cm(
        width_pixels,
        pixels_per_cm
    )

    length_cm = pixel_to_cm(
        height_pixels,
        pixels_per_cm
    )

    chest_cm = max(width_cm * 0.78, length_cm * 0.7)
    shoulder_cm = max(width_cm * 0.42, length_cm * 0.25)
    waist_cm = max(width_cm * 0.58, length_cm * 0.46)
    sleeve_cm = max(length_cm * 0.28, 8.0)

    return {
        "width_cm": round(width_cm, 2),
        "length_cm": round(length_cm, 2),
        "chest_cm": round(chest_cm, 2),
        "shoulder_cm": round(shoulder_cm, 2),
        "waist_cm": round(waist_cm, 2),
        "sleeve_cm": round(sleeve_cm, 2),
    }


def summary_from_measurements(measurements):
    if not measurements:
        return "No measurements available."

    length_cm = float(measurements.get("length_cm", 0.0))
    chest_cm = float(measurements.get("chest_cm", measurements.get("width_cm", 0.0)))
    shoulder_cm = float(measurements.get("shoulder_cm", 0.0))
    waist_cm = float(measurements.get("waist_cm", 0.0))

    lines = [
        "AI size summary:",
        f"Length: {length_cm:.2f} cm",
        f"Chest: {chest_cm:.2f} cm",
        f"Shoulder: {shoulder_cm:.2f} cm",
    ]

    if waist_cm > 0:
        lines.append(f"Waist: {waist_cm:.2f} cm")

    return " | ".join(lines)