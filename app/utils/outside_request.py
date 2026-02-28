import requests
from functools import lru_cache

@lru_cache(maxsize=50)
def validate_artic_place(outside_id: int):
    url = f"https://api.artic.edu/api/v1/artworks/{outside_id}"
    try:
        response = requests.head(url, timeout=5) 
        
        if response.status_code == 200:
            return True
            
        if response.status_code != 200:
            get_response = requests.get(url, timeout=5)
            return get_response.status_code == 200
            
    except requests.RequestException:
        return False
    
    return False