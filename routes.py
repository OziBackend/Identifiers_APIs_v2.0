from flask import jsonify, request, Response

# from helpers import some_helper_function
from controller.dog_controller import (
    dog_breed_identification,
    dog_info_search
)
from controller.insect_controller import (
    insect_identification,
    find_insect_image_and_info
)
from controller.spider_controller import (
    find_spider_image_and_info
)

import threading
import re
import time

from logger.logger import get_logger
#Get configured logger
logger = get_logger()

semaphores = threading.Semaphore(30)


def setup_routes(app):
    @app.route("/")
    def index():
        return "Hello, world!"

    #==========================================================================#
    # Function
    #==========================================================================#

    def check_image(request):
        obj = {}
        if 'image' not in request.files:
            return jsonify({'error': 'No image part found in request'}),400
        
        file = request.files['image']

        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        obj['file'] = file
        return obj, 200
        

    #==========================================================================#
    # Shayari Routes: Identifiers APIs
    #==========================================================================#
    
    @app.route("/identifiers/ai/dog_breed_identifier", methods=["POST"])
    def identify_dog_breed():
        print("Funtion to identify_dog_breed called")

        return_data = {}
        additional_data = {}

        additional_data, status_code = check_image(request)
        
        if status_code != 200:
            return jsonify({'error': 'No image part found in request'}),400
        
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
    
    @app.route("/identifiers/ai/dog_breed_identifier/search_dog_info", methods=["POST"])
    def search_dog_info():
        print("Funtion to search_dog_info called")

        return_data = []
        additional_data = {}

        data = request.get_json()
        breeds = data.get('labels', [])

        if not breeds:
            return jsonify({'error': 'No breeds found in request'}), 400

        additional_data['breeds'] = breeds

        print('Acquiring a Semaphore')
        semaphores.acquire()

        t = threading.Thread(
            target=dog_info_search, args=(app, additional_data, return_data, logger)
        )

        t.start()
        t.join()

        print('Releasing a Semaphore')
        semaphores.release()

        print(return_data)

        if not return_data:
            return jsonify({"response": '' })

        return jsonify(return_data)

    #==========================================================================#

    @app.route("/identifiers/ai/insect_identifier", methods=["POST"])
    def identify_insect():
        print("Funtion to identify_insect called")

        return_data = {}
        additional_data = {}

        additional_data, status_code = check_image(request)
        
        if status_code != 200:
            return jsonify({'error': 'No image part found in request'}),400

        #Acquire Semaphore
        print("Acquiring a Semaphore")
        semaphores.acquire()

        t = threading.Thread(
            target=insect_identification, args=(app, additional_data, return_data, logger)
        )
        
        t.start()
        t.join()

        # Release Semaphore
        print("Releasing a Semaphore")
        semaphores.release()

        # print(return_data)

        if not return_data:
            return jsonify({"response": '' })

        return return_data
    
    @app.route("/identifiers/ai/insect_identifier/find_image_and_info", methods=["POST"])
    def find_insect_image_info():
        print("Funtion to find_insect_image_and_info called")

        return_data = []
        additional_data = {}

        data = request.get_json()
        labels = data.get('labels', [])

        if not labels:
            return jsonify({'error': 'No labels found in request'}), 400

        additional_data['labels'] = labels

        print('Acquiring a Semaphore')
        semaphores.acquire()

        t = threading.Thread(
            target=find_insect_image_and_info, args=(app, additional_data, return_data, logger)
        )

        t.start()
        t.join()

        print('Releasing a Semaphore')
        semaphores.release()

        print(return_data)

        if not return_data:
            return jsonify({"response": '' })

        return jsonify(return_data)

    #==========================================================================#

    @app.route("/identifiers/ai/spider_identifier/find_image_and_info", methods=["POST"])
    def find_spider_image_info():
        print("Funtion to find_spider_image_and_info called")

        return_data = []
        additional_data = {}

        data = request.get_json()
        labels = data.get('labels', [])

        if not labels:
            return jsonify({'error': 'No labels found in request'}), 400

        additional_data['labels'] = labels

        print('Acquiring a Semaphore')
        semaphores.acquire()

        t = threading.Thread(
            target=find_spider_image_and_info, args=(app, additional_data, return_data, logger)
        )

        t.start()
        t.join()

        print('Releasing a Semaphore')
        semaphores.release()

        print(return_data)

        if not return_data:
            return jsonify({"response": '' })

        return jsonify(return_data)