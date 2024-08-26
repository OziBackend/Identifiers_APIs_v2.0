from flask import jsonify, request, Response

# from helpers import some_helper_function
from controller.dog_controller import dog_info_search
from controller.insect_controller import find_insect_image_and_info
from controller.spider_controller import find_spider_image_and_info

import threading

from logger.logger import get_logger
#Get configured logger
logger = get_logger()

semaphores = threading.Semaphore(30)


def setup_routes(app):
    @app.route("/")
    def index():
        return "Hello, world!"

    #==========================================================================#
    # Shayari Routes: Identifiers APIs
    #==========================================================================#
    
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