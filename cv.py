# This file runs a python script which takes an image of a Boggle board and 
# uses computer vision methods to determine the letters!

from imutils.perspective import four_point_transform
import numpy as np
import cv2
from helper_functions import find_averages_of_groups

BOARD_SIZE = 5


############################################
# Get and resize image to lower resolution #
############################################

orig = cv2.imread("raw_data/IMG_5572.jpg")
scale_percent = 20 # percent of original size
width = int(orig.shape[1] * scale_percent / 100)
height = int(orig.shape[0] * scale_percent / 100)
img = cv2.resize(orig, (width, height), interpolation = cv2.INTER_AREA)


########################################
# Get location of board and crop/scale #
########################################

hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
# Threshold of purple boggle board in HSV space
lower_blue = np.array([60, 0, 0])
upper_blue = np.array([240, 255, 255])
mask = cv2.inRange(hsv, lower_blue, upper_blue)
blueimg = cv2.bitwise_and(img, img, mask = mask)
gray = cv2.cvtColor(blueimg, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

boardCnt = None
for c in contours:
  peri = cv2.arcLength(c, True)
  approx = cv2.approxPolyDP(c, 0.02 * peri, True)
  if len(approx) == 4:
    boardCnt = approx
    break

board = four_point_transform(img, boardCnt.reshape(4,2))


#########################################
# Put into black/white and filter image #
#########################################

board = cv2.cvtColor(board, cv2.COLOR_BGR2GRAY)
ret, board = cv2.threshold(board, 120, 255, cv2.THRESH_BINARY)

contours, _ = cv2.findContours(board, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
mask = np.zeros_like(board)
cv2.drawContours(mask, contours, -1, (255, 255, 255), thickness=cv2.FILLED)
board_pre_morph = cv2.bitwise_or(cv2.bitwise_not(mask), board)
cv2.imshow("board_pre_morph", board_pre_morph)

# Perform morphological opening (erodes small black areas and dilates)
board_inverse = cv2.bitwise_not(board_pre_morph)
kernel = np.ones((3, 3),np.uint8) * 255
board_morphed = cv2.morphologyEx(board_inverse, cv2.MORPH_OPEN, kernel)
board_final = cv2.bitwise_not(board_morphed)

cv2.imshow("board_final", board_final)


#########################################
# Split into 25 separate images #
#########################################

# Detect horizontal and vertical white lines (where pixel value is 255)
horizontal_lines = [y for y in range(board_final.shape[0]) if np.all(board_final[y, :] == 255)]

# Detect vertical lines: where each column is entirely white (255)
vertical_lines = [x for x in range(board_final.shape[1]) if np.all(board_final[:, x] == 255)]

horizontal_boundaries = find_averages_of_groups(horizontal_lines)
vertical_boundaries = find_averages_of_groups(vertical_lines)

cv2.imshow("board_final", board_final)

# Now slice the image into 25 smaller images (5x5 grid)
sub_images = []

for i in range(5):
    for j in range(5):
        # Slice the image using the calculated boundaries
        x1, x2 = vertical_boundaries[j], vertical_boundaries[j + 1]
        y1, y2 = horizontal_boundaries[i], horizontal_boundaries[i + 1]
        
        sub_image = board_final[y1:y2, x1:x2]


        non_white_pixels = np.where(sub_image == 0)
        # Get the min and max x and y coordinates that contain the black pixels
        min_x = np.min(non_white_pixels[1])
        max_x = np.max(non_white_pixels[1])
        min_y = np.min(non_white_pixels[0])
        max_y = np.max(non_white_pixels[0])

        # Step 3: Crop the image using the bounding box
        cropped_image = sub_image[min_y:max_y+1, min_x:max_x+1]

        sub_images.append(cropped_image)            
        # Optionally, save each sub-image as a file
        cv2.imshow(f"sub_image_{i}_{j}.png", cropped_image)
    
cv2.waitKey(0)
cv2.destroyAllWindows()
