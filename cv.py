# This file runs a python script which takes an image of a Boggle board and 
# uses computer vision methods to determine the letters!

from imutils.perspective import four_point_transform
from skimage.segmentation import clear_border
import numpy as np
import imutils
import cv2

BOARD_SIZE = 5


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
ret, board = cv2.threshold(board, 140, 255, cv2.THRESH_BINARY)

cv2.imshow("board_crop_thresh", board)


#######################
# Separate into tiles #
#######################

t_length = int(board.shape[0]/BOARD_SIZE)
t_width = int(board.shape[1]/BOARD_SIZE)
tiles = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

CROP_DIST = 0
for i in range(1):
  for j in range(1):
    tile = board[(t_length*i+CROP_DIST):(t_length*(i+1)-CROP_DIST), (t_width*j+CROP_DIST):(t_width*(j+1)-CROP_DIST)]
    
    # Remove black on outside
    contours, _ = cv2.findContours(tile, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask = np.zeros_like(tile)
    cv2.drawContours(mask, contours, -1, (255, 255, 255), thickness=cv2.FILLED)
    tile = cv2.bitwise_or(cv2.bitwise_not(mask), tile)

    y_nonzero, x_nonzero = np.nonzero(255 - tile)
    # tile = tile[np.min(y_nonzero)-5:np.max(y_nonzero)+5, np.min(x_nonzero)-5:np.max(x_nonzero)+5]
    tile = tile[np.min(y_nonzero):np.max(y_nonzero), np.min(x_nonzero):np.max(x_nonzero)]

    tiles[i][j] = tile
    cv2.imshow(f"post{i}{j}", tile)
    

################################
# Prepare image of each letter #
################################

letters = [None]*(26*4)

for i in range(26):  
  letter_image = cv2.imread(f'letters/{chr(ord("a") + i)}.jpg', 0)

  ret, letter_image = cv2.threshold(letter_image, 150, 255, cv2.THRESH_BINARY)

  # Fill in black area outside
  contours, _ = cv2.findContours(letter_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  mask = np.zeros_like(letter_image)
  cv2.drawContours(mask, contours, -1, (255, 255, 255), thickness=cv2.FILLED)
  letter_image = cv2.bitwise_or(cv2.bitwise_not(mask), letter_image)

  # Crop
  y_nonzero, x_nonzero = np.nonzero(255 - letter_image)
  letter_image = letter_image[np.min(y_nonzero):np.max(y_nonzero), np.min(x_nonzero):np.max(x_nonzero)]

  # For each rotation
  for j in range(4):

    letter_image = cv2.rotate(letter_image, cv2.ROTATE_90_CLOCKWISE)

    # Resize
    scale = letter_image.shape[1] / t_width
    letter_width = int(letter_image.shape[1] / scale)
    letter_height = int(letter_image.shape[0] / scale)
    letter_dim = (letter_width, letter_height)
    letter_image = cv2.resize(letter_image, letter_dim, interpolation = cv2.INTER_AREA)

    letters[i*4 + j] = letter_image

    if i == 8:
      cv2.imshow(f"letterimage{i}{j}", letter_image)

  # keypoints, descriptors = sift.detectAndCompute(letter_image, None)
  # letter_images.append(letter_image)
  # letter_kp.append(keypoints)
  # letter_descriptors.append(descriptors)


##################################################
# Overlay images and compare how well they match #
##################################################
correct_letters = ['n', 'm', 'o', 'j', 'r', 's', 'e', 'e', 'j', 's', 'n', 'a', 'g', 'm', 'o', 'd', 'e', 'a', 'm', 'h', 'r', 'e', 'b', 'r', 't']
total_score = 0

for i in range(1):
  for j in range(1):
    best_score = 0
    best_letter = None

    for index, letter in enumerate(letters):

      #TODO: Move sizing into here so it sizes to each letter right before comparison

      resized_letter = cv2.resize(letter, (tiles[i][j].shape[1], tiles[i][j].shape[0]))
      total_matches = np.count_nonzero((resized_letter == 0) & (tiles[i][j] == 0))
      total_black_pixels = max(np.count_nonzero(tiles[i][j] == 0), np.count_nonzero(resized_letter == 0))
      score = total_matches / total_black_pixels
      if score > best_score:
        best_score = score
        best_letter = chr(ord('a') + index//4)
    print(best_letter, best_score)
    if best_letter == correct_letters[i*BOARD_SIZE+j]:
      total_score += 1


print(total_score)


cv2.waitKey(0)
cv2.destroyAllWindows()



# OLD:
#################################################
# For each tile, run SIFT and determine letter! #
#################################################

# for x in range(2):
#   for y in range(2):

#     # gray = cv2.cvtColor(tiles[x][y], cv2.COLOR_BGR2GRAY)
#     gray = tiles[x][y]

#     sift = cv2.SIFT_create()
#     kp, tile_descriptors = sift.detectAndCompute(gray,None)
#     kpimg = cv2.drawKeypoints(gray,kp,img)
#     cv2.imshow(f"kpimg{x}{y}", kpimg)

#     matcher = cv2.BFMatcher()

#     letter_images = []
#     letter_kp = []
#     letter_descriptors = []

#     best_match_index = -1
#     best_match_count = 0

#     for i, descriptors in enumerate(letter_descriptors):
#       matches = matcher.knnMatch(descriptors, tile_descriptors, k=2)

#       # Apply ratio test to filter good matches
#       good_matches = []
#       for m, n in matches:
#         if m.distance < 0.7 * n.distance:
#           good_matches.append(m)

#       if len(good_matches) > best_match_count:
#         best_match_index = i
#         best_match_count = len(good_matches)

#       # All 26 letters
#       if i  in [12, 13, 18, 4]:
#         kpimg2 = cv2.drawKeypoints(letter_images[i],letter_kp[i],img)
#         cv2.imshow(f"letter {i}", kpimg2)  

#     print(f"The matched object is {chr(ord('a') + best_match_index)}")
#     if (chr(ord('a') + best_match_index)) == correct_letters[x*BOARD_SIZE+y]:
#       score += 1

