import joblib
import numpy as np
from PIL import Image
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
from tensorflow.keras.models import load_model
# Load the label encoder
label_encoder = joblib.load("label_encoder.joblib")

# Load the saved model
model = load_model('boggle_model.keras')

# Use the model for prediction or evaluation
#model.summary()

def letter_finder(letter_imgss):
    letterss = []
    for i, letter_imgs in enumerate(letter_imgss):
        letterss.append([])
        for j, letter_img in enumerate(letter_imgs):
            letter_img = np.expand_dims(letter_img, axis=(0, -1))
            letter_pred = model.predict(letter_img)
            letter_pred_indices = np.argmax(letter_pred, axis=1)
            letter = label_encoder.inverse_transform(letter_pred_indices)
            letterss[i].append(letter[0])
    return letterss


# # Directory containing the images
# image_folder = "C:/Users/david/OneDrive - McMaster University/Documents/Side Projects/Boggle/test_data"  # Replace with your folder path

# # Initialize 5x5 lists for images and labels
# images_list = [[None for _ in range(5)] for _ in range(5)]
# labels_list = [[None for _ in range(5)] for _ in range(5)]

# # Sort the images to ensure consistent ordering
# image_files = sorted(os.listdir(image_folder))

# # Iterate over images and populate the lists
# for idx, image_file in enumerate(image_files):
#     # Determine the row and column for 5x5 grid
#     row, col = divmod(idx, 5)
    
#     # Load the image
#     img_path = os.path.join(image_folder, image_file)
#     img = Image.open(img_path).convert("L")  # Convert to grayscale
#     img_array = np.array(img, dtype=np.uint8)
    
#     # Normalize the pixel values to 0 or 1
#     img_binary = (img_array > 128).astype(np.uint8)
    
#     # Get the label from the first character of the filename
#     label = image_file[0].upper()  # Convert to uppercase if needed
    
#     # Populate the lists
#     images_list[row][col] = img_binary
#     labels_list[row][col] = label

#     import random

#     # Flatten the lists to make shuffling easier
#     flattened_images = [img for row in images_list for img in row]
#     flattened_labels = [lbl for row in labels_list for lbl in row]

#     # Combine images and labels into a single list of tuples
#     combined = list(zip(flattened_images, flattened_labels))

#     # Shuffle the combined list
#     random.shuffle(combined)

#     # Unzip the shuffled list back into images and labels
#     shuffled_images, shuffled_labels = zip(*combined)

#     # Reshape back into 5x5 lists
#     shuffled_images_list = [list(shuffled_images[i:i + 5]) for i in range(0, 25, 5)]
#     shuffled_labels_list = [list(shuffled_labels[i:i + 5]) for i in range(0, 25, 5)]

# (shuffled_images_list, shuffled_labels_list)

# print(shuffled_labels_list)

# print(np.array(letter_finder(shuffled_images_list)))




