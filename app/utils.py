import json
import os
from unidecode import unidecode

def ensure_directory_exists(directory):
    """Ensure the specified directory exists"""
    if not os.path.isdir(directory):
        os.makedirs(directory)

def load_json(filepath, default=None):
    """Load JSON data from a file, return default if file doesn't exist"""
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf8") as f:
            return json.load(f)
    return default

def save_json(filepath, data):
    """Save data as JSON to the specified file"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf8") as f:
        json.dump(data, f, ensure_ascii=False)

def find_ingredient(ingredients, name):
    """Find ingredient information in the ingredients list"""
    if name.lower() == "pizza":
        return ("Pizza", "Pizza", "Pizza")

    for ingredient in ingredients:
        if unidecode(name.lower()) in unidecode(ingredient[0].lower()):
            return ingredient

    print(f"Not found: {name}")
    return (f"Not found:{name}", "", "")