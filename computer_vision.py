# This file runs a python script which takes an image of a Boggle board and 
# uses computer vision methods to determine the letters!

from imutils.perspective import four_point_transform
import numpy as np
import cv2
from helper_functions import *
from letter_finder import *
import os

BOARD_SIZE = 5
plot_images = False


def get_sub_images(image, board_image_path=""):

    ############################################
    # Get and resize image to lower resolution #
    ############################################

    orig = image
    scale_percent = 50 # percent of original size
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

    min_area = 1000  # Minimum area threshold
    filtered_contours = [c for c in contours if cv2.contourArea(c) > min_area]
    filtered_contours = sorted(filtered_contours, key=cv2.contourArea, reverse=True)

    # Find the largest quadrilateral
    boardCnt = None
    for c in filtered_contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.01 * peri, True)  # Use smaller epsilon
        if len(approx) == 4:
            boardCnt = approx
            break
    if boardCnt is None:
        print(f"No quadrilateral found for {board_image_path}")
        return

    board = four_point_transform(img, boardCnt.reshape(4,2))
    plot_image("board_initial", board, plot_images)


    #########################################
    # Put into black/white and filter image #
    #########################################

    board = cv2.cvtColor(board, cv2.COLOR_BGR2GRAY)
    _, board = cv2.threshold(board, 120, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(board, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask = np.zeros_like(board)
    cv2.drawContours(mask, contours, -1, (255, 255, 255), thickness=cv2.FILLED)
    board_pre_morph = cv2.bitwise_or(cv2.bitwise_not(mask), board)

    # Perform morphological opening (erodes small black areas and dilates)
    board_inverse = cv2.bitwise_not(board_pre_morph)
    kernel = np.ones((3, 3),np.uint8) * 255
    board_morphed = cv2.morphologyEx(board_inverse, cv2.MORPH_OPEN, kernel)
    board_final = cv2.bitwise_not(board_morphed)

    plot_image("board_final", board_final, plot_images)


    #########################################
    # Split into 25 separate images #
    #########################################

    # Detect horizontal and vertical white lines (where pixel value is 255)
    horizontal_lines = [y for y in range(board_final.shape[0]) if np.all(board_final[y, :] == 255)]

    # Detect vertical lines: where each column is entirely white (255)
    vertical_lines = [x for x in range(board_final.shape[1]) if np.all(board_final[:, x] == 255)]

    horizontal_boundaries = find_averages_of_groups(horizontal_lines)
    vertical_boundaries = find_averages_of_groups(vertical_lines)
    
    if len(horizontal_boundaries) != (BOARD_SIZE + 1) or len(vertical_boundaries) !=  (BOARD_SIZE + 1):
        print(f"Error for {board_image_path}")
        return
    
    ### Debugging code to see how the grid is being created ###
    # for y in horizontal_boundaries:
    #     cv2.line(board_final, (0, y), (board_final.shape[1] - 1, y), (0, 0, 0), 2)  # Black horizontal line
    # for x in vertical_boundaries:
    #     cv2.line(board_final, (x, 0), (x, board_final.shape[1] - 1), (0, 0, 0), 2)  # Black horizontal line
    # cv2.imshow("board_final", board_final)
    # plot_image("board_final_grid", board_final, plot_images)

    image_2D_list = []
    # For each of the 25 tiles
    for i in range(BOARD_SIZE):
        image_2D_list.append([])
        for j in range(BOARD_SIZE):
            # Slice the image using the calculated boundaries
            x1, x2 = vertical_boundaries[j], vertical_boundaries[j + 1]
            y1, y2 = horizontal_boundaries[i], horizontal_boundaries[i + 1]
            sub_image = board_final[y1:y2, x1:x2]
            non_white_pixels = np.where(sub_image == 0)
            # Get the min and max x and y coordinates that contain the black pixels
            if len(non_white_pixels[0]) == 0:
                print("Missing a letter!")
                continue
            min_x = np.min(non_white_pixels[1])
            max_x = np.max(non_white_pixels[1])
            min_y = np.min(non_white_pixels[0])
            max_y = np.max(non_white_pixels[0])
            cropped_image = sub_image[min_y:max_y+1, min_x:max_x+1]

            square_image = make_square_and_resize(cropped_image)
            image_2D_list[i].append(square_image)

    return image_2D_list

def save_training_data(image_2D_list, tile_directory, board_image_path):
    for i, image_row in enumerate(image_2D_list):
        for j, image in enumerate(image_row):
            image_90 = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
            image_180 = cv2.rotate(image, cv2.ROTATE_180)
            image_270 = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
            
            image_name = os.path.splitext(os.path.basename(board_image_path))[0]
            os.makedirs(f"{tile_directory}/tile_{i}_{j}", exist_ok=True) 
            cv2.imwrite(f"{tile_directory}/tile_{i}_{j}/{image_name}_{i}_{j}_A.png", image)
            cv2.imwrite(f"{tile_directory}/tile_{i}_{j}/{image_name}_{i}_{j}_B.png", image_90)
            cv2.imwrite(f"{tile_directory}/tile_{i}_{j}/{image_name}_{i}_{j}_C.png", image_180)
            cv2.imwrite(f"{tile_directory}/tile_{i}_{j}/{image_name}_{i}_{j}_D.png", image_270)


def generate_training_data():
    input_data_folder_path = "raw_data"
    output_data_folder_path = "data_test"
    # Get a list of folder names
    board_names = sorted([f for f in os.listdir(input_data_folder_path) if os.path.isdir(os.path.join(input_data_folder_path, f))])

    # for board in boards:
    for board_name in board_names:
        print(f"Analyzing {board_name}")
        input_board_folder_path = os.path.join(input_data_folder_path, board_name)
        output_board_folder_path = os.path.join(output_data_folder_path, board_name)
        os.makedirs(output_board_folder_path, exist_ok=True)  
        board_image_filenames = sorted([
            f for f in os.listdir(input_board_folder_path)
            if os.path.isfile(os.path.join(input_board_folder_path, f)) and os.path.splitext(f)[1].lower() in {'.jpg', '.jpeg', '.png'}
        ])
        for board_image_filename in board_image_filenames:
            board_image_path = f"{input_board_folder_path}/{board_image_filename}"
            orig = cv2.imread(f"{input_board_folder_path}/{board_image_filename}")
            image_2D_list = get_sub_images(orig, board_image_path)
            if image_2D_list:
                save_training_data(image_2D_list, output_board_folder_path, board_image_path)

    if plot_images:
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def get_25_normalized_images(image):
    print("read image")
    cv2.imwrite("test.jpg", image)
    image_2D_list = get_sub_images(image)
    print("get subimages")
    normalized_array = [[image // 255 for image in row] for row in image_2D_list]
    return normalized_array

### Uncomment the following to generate training data ###
# generate_training_data()
