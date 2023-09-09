#    Copyright 2023 Atick Faisal

#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.


import io
import os
import numpy as np
from PIL import Image
import tensorflow as tf
from flask import Flask, request, jsonify


MODEL_NAME = "cats_and_dogs"
CLASS_NAMES = ["cats", "dogs"]
IMG_SIZE = (160, 160)

if "K_REVISION" in os.environ:
    print("Running on Google Cloud")
    model = tf.keras.models.load_model(f"gs://jetpack-models/{MODEL_NAME}")
else:
    print("Running on a local machine")
    model = tf.keras.models.load_model(f"models/{MODEL_NAME}")


app = Flask(__name__)


@app.route("/", methods=["GET"])
def root():
    return jsonify({"message": "Hello World"})


@app.route("/predict", methods=["POST"])
def predict():
    try:
        # ----------------------- Verify Image ---------------------------
        if "image" not in request.files:
            return jsonify({"error": "No image provided"}), 400

        image_file = request.files["image"]

        allowed_extensions = {'jpg', 'jpeg', 'png'}
        if "." not in image_file.filename or \
                image_file.filename.split('.')[-1].lower() not in allowed_extensions:
            return jsonify({"error": "Invalid image format"}), 400
        # ----------------------------------------------------------------

        image = Image.open(image_file)
        image = image.resize((160, 160))
        image = np.array(image)
        image = np.expand_dims(image, axis=0)

        predictions = model.predict_on_batch(image).flatten()
        predictions = tf.nn.sigmoid(predictions)
        predictions = tf.where(predictions < 0.5, 0, 1)

        response = {
            "class": CLASS_NAMES[predictions[0]]
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
