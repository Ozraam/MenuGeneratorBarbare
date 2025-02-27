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

@app.route('/getMealList', methods=['GET'])
def get_meal_list():
    return jsonify(mealList)

@app.route('/generateImages', methods=['GET'])
def generate_images():
    args = request.args.get('width', default="", type=str).split(" ")
    if args == [""]:
        return jsonify({"error": "No arguments provided"}), 400

    generate_img_from_args(args)
    return jsonify({"message": "Images generated successfully"})

@app.route('/getMailingText', methods=['GET'])
def get_mailing_text():
    with open("build/mail.txt", "r") as f:
        mailing_text = f.read()
    return jsonify({"mailingText": mailing_text})

@app.route('/verticalMenu', methods=['GET'])
def get_image1():
    # if verticalImage is None:
    #     return jsonify({"error": "Image not found"}), 404
    
    # img_io = BytesIO()
    # verticalImage.save(img_io, 'PNG')
    # img_io.seek(0)
    return send_file("build/vertical.png", mimetype='image/png')

@app.route('/horizontalMenu', methods=['GET'])
def get_image2():
    return send_file("build/horizontal.png", mimetype='image/png')

if __name__ == '__main__':
    with open("mealList.json", "r") as f:
        mealList = json.load(f)



    app.run(debug=True, host="0.0.0.0")