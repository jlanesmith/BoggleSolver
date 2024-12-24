
import cv2

# Command-line functions to run to convert HEIC to jpg
# mkdir -p raw_data && for file in raw_data_heic/*.HEIC; do sips -s format jpeg "$file" --out "raw_data/$(basename "${file%.*}.jpg")"; done;


##################################################################################################
# Take in an array of numbers, in groups of consecutive numbers. For each group of consecutive   #
# numbers, calculate the average number. Return an array of the average number of each group,    #
# rounded to an integer. This is used to find lines to separate letters on the board.            #
##################################################################################################

def find_averages_of_groups(nums):
    # Initialize an empty list to store the averages
    averages = []
    
    # Start with the first number in the array
    start = 0
    
    # Traverse the array and find consecutive groups
    for i in range(1, len(nums)):
        # Check if the current number is not consecutive to the previous one
        if nums[i] != nums[i - 1] + 1:
            # If not consecutive, calculate the average of the current group
            group = nums[start:i]
            if len(group) > 10:  # Only consider groups larger than 10
                averages.append(int(sum(group) / len(group)))
            start = i  # Set the start of the next group
    
    # Handle the last group
    group = nums[start:]
    if len(group) > 10:  # Only consider groups larger than 10
        averages.append(int(sum(group) / len(group)))
    
    return averages


def make_square_and_resize(image, size=25):
    # Get the original image dimensions
    height, width = image.shape[:2]
    
    # Calculate padding to make the image square
    if height > width:
        pad_left = (height - width) // 2
        pad_right = height - width - pad_left
        pad_top = 0
        pad_bottom = 0
    else:
        pad_top = (width - height) // 2
        pad_bottom = width - height - pad_top
        pad_left = 0
        pad_right = 0
    
    # Add padding (white space, 255 value)
    padded_image = cv2.copyMakeBorder(image, pad_top, pad_bottom, pad_left, pad_right, cv2.BORDER_CONSTANT, value=255)
    
    # Resize the image to the target size (25x25) without stretching
    resized_image = cv2.resize(padded_image, (size, size), interpolation=cv2.INTER_AREA)
    
    # Ensure that all pixels are either 0 or 255 by applying a final threshold after resizing
    _, final_image = cv2.threshold(resized_image, 127, 255, cv2.THRESH_BINARY)
    
    return final_image


def plot_image(name, image, flag):
    if flag:
        cv2.imshow(name, image)

