from flask import render_template
import json

from functions.googleImagesFunction import fetch_links
from functions.chatgptFunction import search_gpt

import os

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
    
        info=  search_gpt(prompt)
        print(info)
        if not info.strip().endswith('}'):
            info += '}'
        json_info = json.loads(info)
        html_data = render_template('insects.html', **json_info)
        html_data = html_data.replace('\n', '')
        return html_data
    except Exception as e:
        print(f"Error fetching information: {e}")
        return []

#=================================================================#

def find_spider_image_and_info(app, data, return_data, logger):
    with app.app_context(): 
        try:
            spider_names = data.get('labels')

            for spider_name in spider_names:
                # spider_image = fetch_image_links(spider_name + ' spider', 6)
                spider_info = search_info(spider_name)
                
                return_data.append({'spider_name': spider_name, 'spider_info': spider_info})
        except BaseException as e:
            logger.error('3... Exception thrown in find_insect_image_and_info = %s', str(e))
            print(f"3... In find_insect_image_and_info exception is = {e}")
            return_data = []