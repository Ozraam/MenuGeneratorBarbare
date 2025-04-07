from flask import Flask, jsonify, send_file, request
from app.menu_generator import MenuGenerator
from app.cli_parser import CLIParser
from app.utils import load_json, save_json
import os
import time

app = Flask(__name__)

# Constants
BUILD_DIR = "build"
DEFAULT_IMAGE_DIR = "default_img"
MEAL_LIST_FILE = "assets/data/mealList.json"
LAST_MENU_FILE = f"{BUILD_DIR}/last_menu.txt"
MAIL_FILE = f"{BUILD_DIR}/mail.txt"
DEFAULT_MAIL_FILE = f"{DEFAULT_IMAGE_DIR}/mail.txt"

# Load meal list at application startup
def load_meal_list():
    return load_json(MEAL_LIST_FILE, default={})

mealList = load_meal_list()

# Helper functions
def cors_response(response):
    """Add CORS headers to response"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

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

        save_json(LAST_MENU_FILE, last_menu)
        MenuGenerator().generate_menu(last_menu, filename)

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
    last_menu = load_json(LAST_MENU_FILE)
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
    app.run(debug=True, host="0.0.0.0", port=5000)
