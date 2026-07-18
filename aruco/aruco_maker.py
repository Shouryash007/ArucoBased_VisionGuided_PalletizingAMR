import cv2
import cv2.aruco as aruco

# Select dictionary (same as your detection code)
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)

# Marker IDs you want
marker_ids = [4, 5, 6]

# Size of marker image (pixels)
marker_size = 400

for marker_id in marker_ids:
    marker_img = aruco.generateImageMarker(aruco_dict, marker_id, marker_size)

    filename = f"marker_{marker_id}.png"
    cv2.imwrite(filename, marker_img)

    print(f"Saved {filename}")