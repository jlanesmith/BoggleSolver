from flask import Flask, request, jsonify
from PIL import Image, ImageOps
import io
from computer_vision import get_25_normalized_images 
from letter_finder import letter_finder
from word_finder import find_boggle_words
import numpy as np

app = Flask(__name__)

def get_letters(images):
    return letter_finder(images)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "Server is running"}), 200

@app.route('/process-image', methods=['POST'])
def process_image_endpoint():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    image_file = request.files['image']
    try:
        # Open the image using PIL (or any library your script uses)
        image = Image.open(io.BytesIO(image_file.read()))
        r, g, b = image.split()
        # Merge back with channels in corrected order (swap red and blue)
        image = Image.merge('RGB', (b, g, r))

        opencv_image = np.array(image)
        subimages = get_25_normalized_images(opencv_image)
        letters = np.array(get_letters(subimages))
        words = find_boggle_words(letters)
        print(words)
        return jsonify({"words": words})
    except Exception as e:
        print(str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
