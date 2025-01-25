from flask import Flask, request, render_template, jsonify
import os
from tensorflow.keras.models import load_model
import cv2
import numpy as np

app = Flask(__name__)
MODEL_PATH = "pretrained_model.h5"
cnn_model = load_model(MODEL_PATH)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def preprocess_image(image_path):
    img = cv2.imread(image_path)  # Load as RGB
    img = cv2.resize(img, (128, 128))  # Resize to 128x128
    img = img / 255.0  # Normalize to [0, 1]
    return img

def predict_signature(image_path):
    img = preprocess_image(image_path)
    img = img.reshape(1, 128, 128, 3)  # Add batch and channel dimensions
    prob = cnn_model.predict(img)[0][0]  # Get probability of being 'forged'
    return prob

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compare', methods=['POST'])
def compare_signatures():
    try:
        if 'genuineFile' not in request.files or 'forgedFile' not in request.files:
            return jsonify({"error": "Both genuine and forged files must be uploaded."}), 400

        genuine_file = request.files['genuineFile']
        forged_file = request.files['forgedFile']

        print(f"Received files: {genuine_file.filename}, {forged_file.filename}")

        genuine_path = os.path.join(UPLOAD_FOLDER, genuine_file.filename)
        forged_path = os.path.join(UPLOAD_FOLDER, forged_file.filename)

        genuine_file.save(genuine_path)
        forged_file.save(forged_path)

        print(f"Files saved: {genuine_path}, {forged_path}")

        # Predict probabilities
        genuine_prob = float(predict_signature(genuine_path))
        forged_prob = float(predict_signature(forged_path))

        print(f"Genuine probability: {genuine_prob}, Forged probability: {forged_prob}")

        # Compare probabilities and determine result
        if genuine_prob < 0.5 and forged_prob >= 0.5:
            result = "The genuine signature is authentic, and the forged signature is a forgery."
        elif genuine_prob < 0.5 and forged_prob < 0.5:
            result = "Both signatures are marked as genuine."
        elif genuine_prob >= 0.5 and forged_prob >= 0.5:
            result = "Both signatures are marked as forged."
        else:
            result = "The genuine signature appears forged, and the forged signature seems authentic."

        # Return the result as JSON
        return jsonify({
            "result": result,
            "genuine_probability": round(1 - genuine_prob, 2),
            "forged_probability": round(forged_prob, 2)
        })
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": "An error occurred on the server."}), 500


if __name__ == '__main__':
    app.run(debug=True)