import json
import os
import time
from flask import Flask, jsonify, send_file, request
from PIL import Image
from io import BytesIO
from main import generate_img_from_args, CLIParser

app = Flask(__name__)

# Constants
DEFAULT_IMAGE_DIR = "default_img"
BUILD_DIR = "build"
MEAL_LIST_FILE = "mealList.json"
LAST_MENU_FILE = f"{BUILD_DIR}/last_menu.txt"
MAIL_FILE = f"{BUILD_DIR}/mail.txt"
DEFAULT_MAIL_FILE = f"{DEFAULT_IMAGE_DIR}/mail.txt"

# Load meal list at application startup
def load_meal_list():
    try:
        with open(MEAL_LIST_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        app.logger.warning(f"{MEAL_LIST_FILE} not found, using empty dictionary")
        return {}
    except json.JSONDecodeError:
        app.logger.warning(f"{MEAL_LIST_FILE} contains invalid JSON, using empty dictionary")
        return {}

mealList = load_meal_list()

# Helper functions
def cors_response(response):
    """Add CORS headers to response"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

def save_json_to_file(data, filepath):
    """Save data as JSON to the specified file"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf8") as f:
        json.dump(data, f, ensure_ascii=False)

def load_json_from_file(filepath, default=None):
    """Load JSON data from file, return default if file doesn't exist"""
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf8") as f:
            return json.load(f)
    return default

def get_image_path(image_type, epoch):
    """Get the image path based on type and epoch"""
    return f"{BUILD_DIR}/{epoch}-{image_type}.png"

# Routes
@app.route('/getMealList', methods=['GET'])
def get_meal_list():
    response = jsonify(mealList)
    return cors_response(response)

@app.route('/generateImages', methods=['GET'])
def generate_images():
    args = request.args.get('menu', default="", type=str).split(" ")
    
    if args == [""]:
        return cors_response(jsonify({"error": "No arguments provided"})), 400
    
    try:
        last_menu = CLIParser().parse_arguments(args)
        filename = str(int(time.time()))
        
        save_json_to_file(last_menu, LAST_MENU_FILE)
        generate_img_from_args(args, filename)
        
        return cors_response(jsonify({
            "message": "Images generated successfully", 
            "vertical": filename, 
            "horizontal": filename
        }))
    except Exception as e:
        app.logger.error(f"Error generating images: {str(e)}")
        return cors_response(jsonify({"error": str(e)})), 500

@app.route('/getLastMenu', methods=['GET'])
def get_last_menu():
    last_menu = load_json_from_file(LAST_MENU_FILE)
    if last_menu is None:
        return cors_response(jsonify({"error": "No menu generated yet"})), 400
    return cors_response(jsonify(last_menu))

@app.route('/getMailingText', methods=['GET'])
def get_mailing_text():
    try:
        with open(MAIL_FILE, "r", encoding="utf8") as f:
            mailing_text = f.read()
    except FileNotFoundError:
        with open(DEFAULT_MAIL_FILE, "r", encoding="utf8") as f:
            mailing_text = f.read()
    
    return cors_response(jsonify({"text": mailing_text}))

@app.route('/verticalMenu', methods=['GET'])
def get_image1():
    return get_menu_image("vertical")

@app.route('/horizontalMenu', methods=['GET'])
def get_image2():
    return get_menu_image("horizontal")

def get_menu_image(image_type):
    """Handle image retrieval for both vertical and horizontal menus"""
    epoch = request.args.get("epoch", default="", type=str)
    file_name = get_image_path(image_type, epoch)
    
    try:
        return send_file(file_name, mimetype='image/png')
    except FileNotFoundError:
        return send_file(f"{DEFAULT_IMAGE_DIR}/{image_type}.png", mimetype='image/png')

if __name__ == '__main__':
    # This block only runs when executing the script directly (development mode)
    # It won't run when the application is served by Gunicorn
    app.run(debug=True, host="0.0.0.0", port=5000)
