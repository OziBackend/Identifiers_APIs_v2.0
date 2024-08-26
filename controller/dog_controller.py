from datetime import datetime
from PIL import Image
import numpy as np
import tensorflow as tf
from werkzeug.utils import secure_filename
import json
from flask import render_template
import os
import requests
import re

from functions.googleImagesFunction import fetch_links
from functions.groqFunction import search_groq
from functions.chatgptFunction import search_gpt

UPLOAD_FOLDER = 'uploads/dogs'

# Load the TFLite model and allocate tensors.
interpreter = tf.lite.Interpreter(model_path="models/Dog_Training_Data_graph.lite")
interpreter.allocate_tensors()

# Get input and output tensors.
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

#=================================================================#

def load_breed_names():
    # Step 1: Open the file
    with open(r'data_values\dog_free_labels.txt', 'r') as file:
        # Step 2: Read the contents
        contents = file.readlines()

    # Step 3: Remove any trailing newline characters
    array = [line.strip() for line in contents]

    # Step 4: Print the array to verify
    return array
dog_breeds= load_breed_names()

def preprocess_image(image_path, input_size):
    img = Image.open(image_path).convert('RGB')
    img = img.resize(tuple(input_size))
    img = np.array(img, dtype=np.float32)
    img = np.expand_dims(img, axis=0)
    img /= 255.0  # Normalizing the image
    return img

# Function to predict the breed of the dog
def predict_breed(image_path, breeds):
    input_size = input_details[0]['shape'][1:3]  # Assuming model input shape is (1, height, width, 3)
    img = preprocess_image(image_path, input_size)
    
    interpreter.set_tensor(input_details[0]['index'], img)
    interpreter.invoke()
    
    output_data = interpreter.get_tensor(output_details[0]['index'])
    prediction = np.squeeze(output_data)

    print(len(prediction))
    
    # Assuming the model output is a probability distribution over classes
    breed_index = np.argmax(prediction)
    confidence = prediction[breed_index]
    
    print(breed_index)
    print(confidence)
    
    # You should have a list of breed names corresponding to the output classes
    # breed_names = ["breed1", "breed2", "breed3", ...]  # Replace with actual breed names
    
    return breeds[breed_index], confidence

#==================================#

def search_image_links(query, max_links=1):
    try:
        return fetch_links(query, max_links)
    except Exception as e:
        print(e)
        return []
    
def scrap_images(query, max_links=2):
    search_url = f"https://www.google.com/search?tbm=isch&q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(search_url, headers=headers)
    # Get the response content as a string
    html_content = response.text
    
    # Regular expression to find URLs in quotes
    pattern = r'"(https://[^"]+)"'

    # Find all matches in the HTML string
    matches = re.findall(pattern, html_content)

    # List of keywords to filter URLs
    keywords = ["natgeofe.com", "britannica.com", "wikimedia.org", "images.pexels.com", "images.unsplash.com"]

    # List of patterns to ignore
    ignore_patterns = [
        "https://www.britannica.com/animal/", 
        "https://www.google.com/search/about-this-image"
    ]

    # Filter out URLs containing any of the keywords and not containing ignore patterns
    urls_of_interest = [
        url for url in matches 
        if any(keyword in url for keyword in keywords) 
        and not any(ignore in url for ignore in ignore_patterns)
    ]
    urls_of_interest = list(set(urls_of_interest))
    # Limit the number of images
    limited_urls = urls_of_interest[:max_links]

    # print(limited_urls)
    
    return limited_urls

def search_dog_info(prompt_value):
    try:
        prompt = f"""Give me the following information about {prompt_value} breed in dictionary format. The response should only contain the dictionary object, properly formatted. There should be no data other than dict object:
        {{
        "Name": "value",
        "Other_Name": "value",
        "Origin": "value",
        "Breed_Group": "value",
        "Size": "value",
        "Type": "value",
        "Life_Span": "value",
        "Temprament": "value",
        "Height": "value",
        "Weight": "value",
        "Colors": "value"
        }}
        """
        info =search_gpt(prompt)
        if not info.strip().endswith('}'):
            info = info + '}'
        json_info = json.loads(info)
        html_data = render_template('dogs.html', **json_info)
        return html_data
    except Exception as e:
        print(e)
        return []
    

#=================================================================#

def dog_breed_identification(app, data, return_data, logger):

    with app.app_context():
        try:
            file = data['file']

            if file:
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                print(file_path)

                breed, confidence = predict_breed(file_path, dog_breeds)
                return_data['response']= f"The predicted breed is {breed} with probability {confidence*100:.2f}"
                logger.info(f"The predicted breed is {breed} with probability {confidence*100:.2f}")
                return_data['breed']= breed
                # return_data['confidence']= confidence
                # return_data['response']= ""

            return {'breed name'}
        except BaseException as e:
            logger.error('1... Exception thrown in dog_breed_identification = %s', str(e))
            print(f"1... In dog_breed_identification exception is = {e}")
            return_data['response']= ''

def dog_info_search(app, data, return_data, logger):
    with app.app_context():
        try:
            dog_breeds = data.get('breeds')

            for breed in dog_breeds:
                dog_info = search_dog_info(breed)
                return_data.append({'dog_breed': breed, 'dog_info': dog_info})
        except BaseException as e:
            logger.error('1... Exception thrown in dog_info_search = %s', str(e))
            print(f"1... In dog_info_search exception is = {e}")
            return_data=[]