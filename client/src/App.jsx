// Copyright 2023 Atick Faisal

// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at

//     http://www.apache.org/licenses/LICENSE-2.0

// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import { useState } from "react";
import placeholder from "./assets/placeholder.svg";
import "./App.css";

function App() {
    const [prediction, setPrediction] = useState("None");
    const [loading, setLoading] = useState(false);
    const [image, setImage] = useState(placeholder);
    const [imageFile, setImageFile] = useState(null);

    const uploadImage = async () => {
        setLoading(true);
        const formData = new FormData();
        formData.append("image", imageFile);
        try {
            const response = await fetch("/predict", {
                method: "POST",
                body: formData,
            });
            if (response.ok) {
                const data = await response.json();
                setPrediction(data.class);
                console.log(data);
            } else {
                console.error("Server Error: ", response.status);
            }
        } catch (error) {
            setPrediction(error)
            console.error("Error: ", error);
        } finally {
            setLoading(false);
        }
    };

    const onSelectImage = (e) => {
        const file = e.target.files?.[0];
        if (file) {
            setImageFile(file);
            setPrediction("None");
            const reader = new FileReader();
            reader.onload = (event) => {
                if (event.target) {
                    setImage(event.target.result);
                }
            };
            reader.readAsDataURL(file);
        } else {
            setImage(placeholder);
        }
    };

    return (
        <div className="container">
            <div className="content">
                <h4 className="label">Prediction: {prediction}</h4>
                <div>
                    <input
                        accept="image/*"
                        className="SelectImage"
                        style={{ display: "none" }}
                        id="image-selector"
                        multiple
                        type="file"
                        onChange={onSelectImage}
                    />
                    <label htmlFor="image-selector">
                        <img
                            style={{ width: "100%" }}
                            src={image}
                            alt="image"
                        />
                    </label>
                </div>
                <button aria-busy={loading} onClick={uploadImage}>
                    Upload
                </button>
            </div>
        </div>
    );
}

export default App;
