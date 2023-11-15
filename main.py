"""
    Copyright 2023 Atick Faisal

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""


import io
import os
import uuid
import keras
import numpy as np
from PIL import Image
import tensorflow as tf
from google.cloud import storage
from flask import Flask, request, jsonify, send_from_directory

BUCKET_NAME = "jetpack-ai-data"
STORAGE_NAME = "cats-and-dogs"
MODEL_NAME = "cats_and_dogs"
CLASS_NAMES = ["cats", "dogs"]
IMG_SIZE = (160, 160)

if "K_REVISION" in os.environ:
    print("Running on Google Cloud")
    model = keras.models.load_model(
        f"gs://{BUCKET_NAME}/{STORAGE_NAME}/model/{MODEL_NAME}")
else:
    print("Running on a local machine")
    model = keras.models.load_model(f"models/{MODEL_NAME}")


app = Flask(__name__, static_folder="client")

storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET_NAME)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    """
    Serves static files or the index.html file.

    Args:
        path (str): The path to the file to serve.

    Returns:
        flask.Response: The response containing the requested file or index.html.
    """
    if path != "" and os.path.exists(app.static_folder + "/" + path):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")


@app.route("/predict", methods=["POST"])
def predict():
    """
    Endpoint for image prediction.

    Accepts an image file, processes it, and returns a prediction.

    Returns:
        flask.Response: A JSON response containing the prediction.
    """
    try:
        # ----------------------- Verify Image ---------------------------
        if "image" not in request.files:
            return jsonify({"error": "No image provided"}), 400

        image_file = request.files["image"]

        allowed_extensions = {"jpg", "jpeg", "png"}
        image_extension = image_file.filename.split(".")[-1].lower()
        if "." not in image_file.filename or \
                image_extension not in allowed_extensions:
            return jsonify({"error": "Invalid image format"}), 400
        # ----------------------------------------------------------------

        image = Image.open(image_file)
        image_rgb = image.convert("RGB")
        image_resized = image_rgb.resize((160, 160))
        image_numpy = np.array(image_resized)
        image_batch = np.expand_dims(image_numpy, axis=0)

        predictions = model.predict_on_batch(image_batch).flatten()
        predictions = tf.nn.sigmoid(predictions)
        predictions = tf.where(predictions < 0.5, 0, 1)

        # ----------------------- Save Image ------------------------------
        if image_extension in ("jpg", "jpeg"):
            image_format = "JPEG"
            content_type = "image/jpeg"
        else:
            image_format = "PNG"
            content_type = "image/png"

        blob = bucket.blob(
            f"{STORAGE_NAME}/images/{str(uuid.uuid4())}.{image_extension}")
        image_byte_array = io.BytesIO()
        image.save(image_byte_array, format=image_format)
        blob.upload_from_string(
            image_byte_array.getvalue(), content_type=content_type)
        # -----------------------------------------------------------------

        response = {
            "class": CLASS_NAMES[predictions[0]]
        }

        return jsonify(response), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 500

    except OSError as error:
        return jsonify({"error": str(error)}), 500


@app.route("/health_check", methods=["GET"])
def health_check():
    """
    Health check endpoint.

    Returns:
        flask.Response: A JSON response with a "Hello World" message.
    """
    return jsonify({"message": "Hi Mom"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
