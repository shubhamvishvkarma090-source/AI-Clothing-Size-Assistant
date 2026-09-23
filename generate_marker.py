import cv2

dictionary = cv2.aruco.getPredefinedDictionary(
    cv2.aruco.DICT_4X4_50
)

marker = cv2.aruco.generateImageMarker(
    dictionary,
    0,
    1000
)

cv2.imwrite("marker.png", marker)

print("marker.png created")