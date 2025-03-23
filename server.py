import json
import os
import time
from flask import Flask, jsonify, send_file, request
from PIL import Image
from io import BytesIO
from main import generate_img_from_args, cli_process

app = Flask(__name__)

# Load meal list at application startup
mealList = {}
try:
    with open("mealList.json", "r") as f:
        mealList = json.load(f)
except FileNotFoundError:
    app.logger.warning("mealList.json not found, using empty dictionary")
except json.JSONDecodeError:
    app.logger.warning("mealList.json contains invalid JSON, using empty dictionary")

def cors_response(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/getMealList', methods=['GET'])
def get_meal_list():
    response = jsonify(mealList)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/generateImages', methods=['GET'])
def generate_images():
    args = request.args.get('menu', default="", type=str).split(" ")
    
    last_menu = cli_process(args)

    filename = int(time.time())

    with open("build/last_menu.txt", "w", encoding="utf8") as f:
        json.dump(last_menu, f, ensure_ascii=False)

    if args == [""]:
        return jsonify({"error": "No arguments provided"}), 400
    try:
        generate_img_from_args(args, filename)
    except Exception as e:
        print(e)
        return cors_response(jsonify({"error": str(e)})), 500
    return cors_response(jsonify({"message": "Images generated successfully", "vertical": f"{filename}", "horizontal": f"{filename}"}))

@app.route('/getLastMenu', methods=['GET'])
def get_last_menu():
    if os.path.exists("build/last_menu.txt"):
        with open("build/last_menu.txt", "r", encoding="utf8") as f:
            last_menu = json.load(f)
    else:
        last_menu = None

    if last_menu is None:
        return cors_response(jsonify({"error": "No menu generated yet"})), 400
    return cors_response(jsonify(last_menu))



@app.route('/getMailingText', methods=['GET'])
def get_mailing_text():
    try:
        with open("build/mail.txt", "r", encoding="utf8") as f:
            mailing_text = f.read()
    except FileNotFoundError:
        with open("default_img/mail.txt", "r", encoding="utf8") as f:
            mailing_text = f.read()
    
    response = jsonify({"text": mailing_text})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/verticalMenu', methods=['GET'])
def get_image1():
    epoch = request.args.get("epoch", default="", type=str)

    file_name = f"build/{epoch}-vertical.png"
    # check if the file exists else send default image
    try:
        return send_file(file_name, mimetype='image/png')
    except FileNotFoundError:
        return send_file("default_img/vertical.png", mimetype='image/png')


@app.route('/horizontalMenu', methods=['GET'])
def get_image2():
    epoch = request.args.get("epoch", default="", type=str)

    file_name = f"build/{epoch}-horizontal.png"
    # check if the file exists else send default image
    try:
        return send_file(file_name, mimetype='image/png')
    except FileNotFoundError:
        return send_file("default_img/horizontal.png", mimetype='image/png')

if __name__ == '__main__':

    # This block only runs when executing the script directly (development mode)
    # It won't run when the application is served by Gunicorn
    app.run(debug=True, host="0.0.0.0", port=5000)
