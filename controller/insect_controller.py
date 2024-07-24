from datetime import datetime
from PIL import Image
import numpy as np
import tensorflow as tf
from werkzeug.utils import secure_filename
import os
import requests

#===================Configuration For GROQ API======================#
os.environ["GROQ_API_KEY"] = (
    "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"  # Replace with your actual key
)
from groq import Groq
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

#===================Configuration For Google API===================#
# Replace these with your own API key 
# and Custom Search Engine ID
API_KEY = 'AIzaSyBDtuFLLgG7x7CBiriNxiQxYiJ3jSkDqac'
CX = '831bd8939aba44ce8'
QUERY = ''

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

#Fetch images from google
def fetch_links(query, max_links=10):
    try:
        url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={CX}&q={query}&searchType=image"
        response = requests.get(url)
        data = response.json()
        images = [item['link'] for item in data.get('items', [])]
        return images[:max_links]  # Limit the number of links
    except Exception as e:
        print(f"Error fetching images: {e}")
        return []

#Fetch information from groq
def search_groq(prompt_value):
    try:
        prompt = f'Give me information about {prompt_value} in 2 lines'
    
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
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

                
                QUERY = insect

                #Fetch Limited number of images
                images = fetch_links(QUERY, 5)
                return_data['images']= images

                #Fetch information about the insect
                information = search_groq(QUERY)
                return_data['information']= information

                
                logger.info(f"The predicted insect is {insect} with probability {confidence*100:.2f}")
        except BaseException as e:
            logger.error('2... Exception thrown in insect_identification = %s', str(e))
            print(f"2... In insect_identification exception is = {e}")
            return_data['confidence']= '0.00'

def find_insect_image_and_info(app, data, return_data, logger):
    with app.app_context(): 
        try:
            insect_names = data.get('labels')

            for insect_name in insect_names:
                obj = {}
                insect_image = fetch_links(insect_name, 1)
                insect_info = search_groq(insect_name)
                obj['insect_name'] = insect_name
                obj['insect_image'] = insect_image
                obj['insect_info'] = insect_info
                return_data.append(obj)
        except BaseException as e:
            logger.error('3... Exception thrown in find_insect_image_and_info = %s', str(e))
            print(f"3... In find_insect_image_and_info exception is = {e}")
            return_data = []