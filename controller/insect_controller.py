from datetime import datetime
from PIL import Image
import numpy as np
import tensorflow as tf
from werkzeug.utils import secure_filename
from flask import render_template
import json

from functions.googleImagesFunction import fetch_links
from functions.groqFunction import search_groq

import os

#=================================================================#
UPLOAD_FOLDER = 'uploads/insects'

# Load the TFLite model and allocate tensors.
interpreter = tf.lite.Interpreter(model_path="models/InsectModel.tflite")
interpreter.allocate_tensors()

# Get input and output tensors.
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

#===========================FUNCTIONS============================#
def load_insect_names():
    # Step 1: Open the file
    with open(r'data_values\InsectLabelsNew.txt', 'r') as file:
        # Step 2: Read the contents
        contents = file.readlines()

    # Step 3: Remove any trailing newline characters
    array = [line.strip() for line in contents]

    # Step 4: Print the array to verify
    return array
insect_types= load_insect_names()
print(len(insect_types))

#preprocess an image
def preprocess_image(image_path, input_size):
    img = Image.open(image_path).convert('RGB')
    img = img.resize(tuple(input_size))
    img = np.array(img, dtype=np.uint8)
    img = np.expand_dims(img, axis=0)
    # img /= 255.0  # Normalizing the image
    return img

# Function to predict the breed of the dog
def predict_insect(image_path, insects):
    input_size = input_details[0]['shape'][1:3]  # Assuming model input shape is (1, height, width, 3)
    img = preprocess_image(image_path, input_size)
    
    interpreter.set_tensor(input_details[0]['index'], img)
    interpreter.invoke()
    
    output_data = interpreter.get_tensor(output_details[0]['index'])
    prediction = np.squeeze(output_data)

    print(len(prediction))
    
    # Assuming the model output is a probability distribution over classes
    insect_index = np.argmax(prediction)
    confidence = prediction[insect_index]
    
    print(insect_index)
    print(confidence)
    
    # You should have a list of breed names corresponding to the output classes
    # insects[index]
    return insects[insect_index], confidence

#=========================#

#Fetch images from google
def fetch_image_links(query, max_links=10):
    try:
        return fetch_links(query, max_links)
    except Exception as e:
        print(f"Error fetching images: {e}")
        return []

#Fetch information from groq
def search_info(prompt_value):
    try:
        prompt = f"""Give me the following information about {prompt_value} in dictionary format. The response should only contain the dictionary object, properly formatted. There should be no data other than dict object:
        {{
        "Common_Name": "value",
        "Scientific_Name": "value",
        "Size": "value",
        "Color": "value",
        "Shape": "value",
        "Habitat": "value",
        "Diet": "value",
        "Role_in_Ecosystem": "value",
        "Interesting_Fact": "value"
        }}
        """
    
        info=  search_groq(prompt)
        if not info.strip().endswith('}'):
            info += '}'
        json_info = json.loads(info)
        html_data = render_template('insects.html', **json_info)
        return html_data
    except Exception as e:
        print(f"Error fetching information: {e}")
        return []

#=================================================================#
def insect_identification(app, data, return_data, logger):

    with app.app_context():
        try:
            file = data['file']

            if file:
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                print(file_path)

                insect, confidence = predict_insect(file_path, insect_types)
                return_data['insect']= insect
                return_data['confidence']= f'{confidence:.2f}'

                
                query_value = insect

                #Fetch Limited number of images
                images = fetch_image_links(query_value, 5)
                return_data['images']= images

                #Fetch information about the insect
                information = search_info(query_value)
                return_data['information']= information

                
                logger.info(f"The predicted insect is {insect} with probability {confidence*100:.2f}")
        except BaseException as e:
            logger.error('2... Exception thrown in insect_identification = %s', str(e))
            print(f"2... In insect_identification exception is = {e}")
            return_data['confidence']= '0.00'

#=======================#

def find_insect_image_and_info(app, data, return_data, logger):
    with app.app_context(): 
        try:
            insect_names = data.get('labels')

            for insect_name in insect_names:
                insect_image = fetch_image_links(insect_name, 6)
                insect_info = search_info(insect_name)
                
                return_data.append({'insect_name': insect_name, 'insect_image': insect_image, 'insect_info': insect_info})
        except BaseException as e:
            logger.error('3... Exception thrown in find_insect_image_and_info = %s', str(e))
            print(f"3... In find_insect_image_and_info exception is = {e}")
            return_data = []