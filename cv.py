# This file runs a python script which takes an image of a Boggle board and 
# uses computer vision methods to determine the letters!

from imutils.perspective import four_point_transform
from skimage.segmentation import clear_border
import numpy as np
import imutils
import cv2


########################
# Get and resize image #
########################

orig = cv2.imread("demo.png")
scale_percent = 20 # percent of original size
width = int(orig.shape[1] * scale_percent / 100)
height = int(orig.shape[0] * scale_percent / 100)
dim = (width, height)
img = cv2.resize(orig, dim, interpolation = cv2.INTER_AREA)


#########################
# Get location of board #
#########################

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
board = board[20:board.shape[0]-20, 20:board.shape[1]-20]
board = cv2.cvtColor(board, cv2.COLOR_BGR2GRAY)
# board = cv2.GaussianBlur(board, (7, 7), 3)
# board = cv2.adaptiveThreshold(board, 255,
		# cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 5, 3)
# board = cv2.bitwise_not(board)

cv2.imshow("board_crop", board)


#######################
# Separate into tiles #
#######################

t_length = int(board.shape[0]/5)
t_width = int(board.shape[1]/5)
tiles = [[None for _ in range(5)] for _ in range(5)]

CROP_DIST = 5
for i in range(5):
  for j in range(5):
    tiles[i][j] = board[(t_length*i+CROP_DIST):(t_length*(i+1)-CROP_DIST), (t_width*j+CROP_DIST):(t_width*(j+1)-CROP_DIST)]

# for i in range(1,5):
#   board = cv2.line(board, (t_width*i,0), (t_width*i,t_length*5), (0,255,0), 3)
# for j in range(1,5):
#   board = cv2.line(board, (0,t_length*j), (t_width*5,t_length*j), (0,255,0), 3)
# cv2.imshow("board_with_lines", board)


#################################################
# For each tile, run SIFT and determine letter! #
#################################################

correct_letters = ['n', 'm', 'o', 'j', 'r', 's', 'e', 'e', 'j', 's', 'n', 'a', 'g', 'm', 'o', 'd', 'e', 'a', 'm', 'h', 'r', 'e', 'b', 'r', 't']
score = 0
# for x in range(2,3):
#   for y in range(4,5):
for x in range(5):
  for y in range(5):

    # gray = cv2.cvtColor(tiles[x][y], cv2.COLOR_BGR2GRAY)
    gray = tiles[x][y]

    sift = cv2.SIFT_create()
    kp, tile_descriptors = sift.detectAndCompute(gray,None)
    kpimg=cv2.drawKeypoints(gray,kp,img)
    cv2.imshow(f"kpimg{x}{y}", kpimg)

    # Create FLANN matcher
    # FLANN_INDEX_KDTREE = 1
    # index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    # search_params = dict(checks=50)
    # matcher = cv2.FlannBasedMatcher(index_params, search_params)
    matcher = cv2.BFMatcher()

    letter_images = []
    letter_kp = []
    letter_descriptors = []

    # Load and compute keypoints and descriptors for each letter image
    for i in range(26):  
      letter_image = cv2.imread(f'letters/{chr(ord("a") + i)}.jpg', 0)

      scale = letter_image.shape[1] / t_width
      letter_width = int(letter_image.shape[1] / scale)
      letter_height = int(letter_image.shape[0] / scale)
      letter_dim = (letter_width, letter_height)
      letter_image = cv2.resize(letter_image, letter_dim, interpolation = cv2.INTER_AREA)

      keypoints, descriptors = sift.detectAndCompute(letter_image, None)
      letter_images.append(letter_image)
      letter_kp.append(keypoints)
      letter_descriptors.append(descriptors)

    best_match_index = -1
    best_match_count = 0

    for i, descriptors in enumerate(letter_descriptors):
      matches = matcher.knnMatch(descriptors, tile_descriptors, k=2)

      # Apply ratio test to filter good matches
      good_matches = []
      for m, n in matches:
        if m.distance < 0.7 * n.distance:
          good_matches.append(m)

      if len(good_matches) > best_match_count:
        best_match_index = i
        best_match_count = len(good_matches)

      # All 26 letters
      # if i == 20:
      #   kpimg2=cv2.drawKeypoints(letter_images[i],letter_kp[i],img)
      #   cv2.imshow(f"kpimg {i}", kpimg2)  

    print(f"The matched object is {chr(ord('a') + best_match_index)}")
    if (chr(ord('a') + best_match_index)) == correct_letters[x*5+y]:
      score += 1


print(score)

cv2.waitKey(0)
cv2.destroyAllWindows()