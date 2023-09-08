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
from starlette.responses import JSONResponse
from fastapi import FastAPI, File, UploadFile


if "K_REVISION" in os.environ:
    print("Running on Google Cloud")
    model = tf.keras.models.load_model("gs://jetpack-models/cats_and_dogs")
else:
    print("Running on a local machine")
    model = tf.keras.models.load_model("models/cats_and_dogs")

class_names = ["cats", "dogs"]

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/predict")
async def predict(file: UploadFile):
    image = Image.open(io.BytesIO(await file.read()))
    image = image.resize((160, 160))
    image = np.array(image)
    image = np.expand_dims(image, axis=0)

    predictions = model.predict_on_batch(image).flatten()
    predictions = tf.nn.sigmoid(predictions)
    predictions = tf.where(predictions < 0.5, 0, 1)

    return JSONResponse({"class": class_names[predictions[0]]})
