import json
from flask import Flask, jsonify, send_file, request
from PIL import Image
from io import BytesIO
from main import generate_img_from_args, cli_process

app = Flask(__name__)

verticalImage : Image = None
horizontalImage : Image = None
mail = ""

mealList = {}

last_menu = None

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

    if args == [""]:
        return jsonify({"error": "No arguments provided"}), 400
    try:
        generate_img_from_args(args)
    except Exception as e:
        return cors_response(jsonify({"error": str(e)})), 500
    return cors_response(jsonify({"message": "Images generated successfully"}))

@app.route('/getLastMenu', methods=['GET'])
def get_last_menu():
    if last_menu is None:
        return jsonify({"error": "No menu generated yet"}), 400
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
    file_name = "build/vertical.png"
    # check if the file exists else send default image
    try:
        return send_file(file_name, mimetype='image/png')
    except FileNotFoundError:
        return send_file("default_img/vertical.png", mimetype='image/png')


@app.route('/horizontalMenu', methods=['GET'])
def get_image2():
    file_name = "build/horizontal.png"
    # check if the file exists else send default image
    try:
        return send_file(file_name, mimetype='image/png')
    except FileNotFoundError:
        return send_file("default_img/horizontal.png", mimetype='image/png')

if __name__ == '__main__':
    with open("mealList.json", "r") as f:
        mealList = json.load(f)


    app.run(debug=True, host="0.0.0.0")