import cv2

IMAGE_PATH = "images/shirt.jpg"

image = cv2.imread(IMAGE_PATH)

if image is None:
    print("ERROR: Image not found")
    exit()

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

dictionary = cv2.aruco.getPredefinedDictionary(
    cv2.aruco.DICT_4X4_50
)

parameters = cv2.aruco.DetectorParameters()

detector = cv2.aruco.ArucoDetector(
    dictionary,
    parameters
)

corners, ids, rejected = detector.detectMarkers(
    gray
)

print("Detected IDs:", ids)
print("Rejected markers:", len(rejected))

if ids is not None:

    print("SUCCESS! ArUco marker detected.")

    output = image.copy()

    cv2.aruco.drawDetectedMarkers(
        output,
        corners,
        ids
    )

    cv2.imwrite(
        "results/marker_test.jpg",
        output
    )

    cv2.imshow(
        "Detected Marker",
        output
    )

    cv2.waitKey(0)
    cv2.destroyAllWindows()

else:

    print("FAILED: ArUco marker not detected.")

    cv2.imshow(
        "Original Image",
        image
    )

    cv2.waitKey(0)
    cv2.destroyAllWindows()