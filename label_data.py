import os
import cv2
import time
from collections import defaultdict

# Directory setup
base_path = '/Users/jonathanlanesmith/Code/BoggleSolver/data/'

# A dictionary to keep track of existing letter counts for renaming
letter_counts = defaultdict(int)

def rename_tile_folders():
    # Get all directories inside the 'data' folder
    board_folders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f)) and f.startswith('board')]
    
    # Iterate through each board folder
    for board_folder in board_folders:
        board_path = os.path.join(base_path, board_folder)
        
        # Iterate through each tile_i_j folder (only folders starting with 'tile')
        for folder_name in os.listdir(board_path):
            if folder_name.startswith('tile_'):  # Only process folders that start with 'tile_'
                tile_folder = os.path.join(board_path, folder_name)

                if not os.path.isdir(tile_folder):
                    continue
                
                # Find an image in the folder (any image will do)
                image_files = [f for f in os.listdir(tile_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                
                if not image_files:
                    continue
                
                # Load the image
                image_path = os.path.join(tile_folder, image_files[0])
                img = cv2.imread(image_path)
                
                # Resize the image to 4 times its original size
                img_resized = cv2.resize(img, (img.shape[1] * 4, img.shape[0] * 4))
                
                # Display the image using OpenCV
                cv2.imshow('Tile Image', img_resized)

                # Wait for 1 second (1000 ms) while the image stays up
                cv2.waitKey(100)

                # Close the image window after the 1 second
                cv2.destroyAllWindows()

                # Ask the user for a letter to rename the folder
                letter = input(f"Enter a letter for {folder_name} (current folder: {tile_folder}): ").strip()
                
                # Check if the letter already exists, and if so, increment the number
                if letter_counts[letter] > 0:
                    letter += str(letter_counts[letter])
                
                # Check if the folder with the new name already exists, and if so, add a number to it
                new_folder = os.path.join(board_path, letter)
                while os.path.exists(new_folder):
                    # If the folder exists, append a number and check again
                    letter_counts[letter] += 1
                    new_folder = os.path.join(board_path, f"{letter[:-1]}{letter_counts[letter]}")
                
                # Rename the folder
                try:
                    os.rename(tile_folder, new_folder)
                    print(f"Renamed {tile_folder} to {new_folder}")
                    
                    # Update the letter count
                    letter_counts[letter] += 1
                except OSError as e:
                    print(f"Error renaming {tile_folder} to {new_folder}: {e}")

# Run the script
rename_tile_folders()
