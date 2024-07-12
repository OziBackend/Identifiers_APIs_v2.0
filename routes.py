from flask import jsonify, request, Response

# from helpers import some_helper_function
from controller.controller import (
    dog_breed_identification
)
import threading
import re
import time

from logger.logger import get_logger
#Get configured logger
logger = get_logger()

semaphores = threading.Semaphore(30)


def setup_routes(app):
    @app.route("/identifiers/ai")
    def index():
        return "Hello, world!"

    #==========================================================================#
    # Shayari Routes: Urdu Shayari APIs using ChatGPT
    #==========================================================================#
    
    @app.route("/identifiers/ai/dog_breed_identifier", methods=["POST"])
    def identify_dog_breed():
        print("Funtion to identify_dog_breed called")

        
        if 'image' not in request.files:
            return jsonify({'error': 'No image part found in request'}),400
        
        file = request.files['image']

        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        logger.info(f"API called 'identify_dog_breed'")

        return_data = {}
        additional_data = {
            "file": file
        }
        
        # Acquire Semaphore
        print("Acquiring a Semaphore")
        semaphores.acquire()

        t = threading.Thread(
            target=dog_breed_identification, args=(app, additional_data, return_data, logger)
        )
        t.start()
        t.join()

        # Processing on response
        print(return_data)

        # Release Semaphore
        print("Releasing a Semaphore")
        semaphores.release()

        if not return_data:
            return jsonify({"response": '' })

        return jsonify(return_data)
    
