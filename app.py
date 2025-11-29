import os
from flask import Flask, request, render_template, redirect, url_for
import cv2
from inference_sdk import InferenceHTTPClient

app = Flask(__name__)

# Initialize the client
CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="iyPThwgorhL35k1j1t76"
)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        wall_age = int(request.form['wall_age'])
      #  wall_wet = request.form['wall_wet']
       # water_fixing = request.form['water_fixing']
        image_file = request.files['image']
        
        if image_file:
            # Ensure the static directory exists
            static_dir = os.path.join(app.root_path, 'static')
            if not os.path.exists(static_dir):
                os.makedirs(static_dir)

            # Save the uploaded image to the static directory
            image_path = os.path.join(static_dir, 'uploaded_image.jpg')
            image_file.save(image_path)
            image = cv2.imread(image_path)
            
            # Perform inference
            result = CLIENT.infer(image, model_id="urabn-roof/1")
            
            # Render the result page
            return render_template('result.html', result=result)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
