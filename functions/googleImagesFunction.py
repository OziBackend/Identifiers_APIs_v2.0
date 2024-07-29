import requests

#===================Configuration For Google API===================#
# Replace these with your own API key 
# and Custom Search Engine ID
API_KEY = 'AIzaSyBDtuFLLgG7x7CBiriNxiQxYiJ3jSkDqac'
CX = '831bd8939aba44ce8'

def fetch_links(query, num_results):
    try:
        url = f'https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={CX}&q={query}&num={num_results}&searchType=image'
        response = requests.get(url)
        data = response.json()
        images = [item['link'] for item in data['items']]
        return images
    except Exception as e:
        print(e)
        return []