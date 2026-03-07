from flask import Flask, jsonify, request
from flask_cors import CORS
import base64
import prediction
import cv2
import numpy as np
import traceback

app = Flask(__name__)
CORS(app)

@app.route('/predict-batch', methods=['POST'])
def predict_batch():
    try:
        files = request.files.getlist("images")

        if not files:
            return jsonify({"error": "No images provided"}), 400

        batch_results = []

        for file in files:
            file_bytes = np.frombuffer(file.read(), np.uint8)
            image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            predicted_image, classes = prediction.predict(image)

            _, buffer = cv2.imencode('.png', predicted_image)
            img_base64 = base64.b64encode(buffer).decode('utf-8')

            batch_results.append({
                "predicted_image": img_base64,
                "classes": classes.tolist()
            })

        return jsonify(batch_results)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
        
@app.route('/predict', methods=['POST'])
def predict_route():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"})

        file = request.files['image']

        image = cv2.imdecode(
            np.frombuffer(file.read(), np.uint8),
            cv2.IMREAD_COLOR
        )

        if image is None:
            return jsonify({"error": "Failed to decode uploaded image"})

        predicted_image, classes = prediction.predict(image)

        # Save input and output (optional)
        cv2.imwrite("uploaded_input.jpg", image)

        if predicted_image is not None:
            cv2.imwrite("prediction_output.png", predicted_image)

        _, buffer = cv2.imencode('.png', predicted_image)
        img_base64 = base64.b64encode(buffer).decode('utf-8')

        return jsonify({
            'predicted_image': img_base64,
            'classes': classes.tolist()
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    print("Initializing model...")
    prediction.initalize_model()
    print("Model loaded successfully.")

    app.run(debug=False, port=5000)