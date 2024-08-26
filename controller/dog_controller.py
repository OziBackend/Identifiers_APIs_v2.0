import json
from flask import render_template


from functions.chatgptFunction import search_gpt

#=================================================================#

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