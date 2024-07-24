from datetime import datetime
from PIL import Image
import numpy as np
import tensorflow as tf
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = 'uploads/dogs'

# Load the TFLite model and allocate tensors.
interpreter = tf.lite.Interpreter(model_path="models/Dog_Training_Data_graph.lite")
interpreter.allocate_tensors()

# Get input and output tensors.
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

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