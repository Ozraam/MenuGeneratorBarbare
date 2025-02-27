import json
from time import sleep
from PIL import Image, ImageDraw, ImageFont
from datetime import date, timedelta
import locale
from unidecode import unidecode
import os

LOGO = "Barbare.png"

## Return the date of the next monday and the date of the next friday in the format "Semaine du 01 au 05 mars 2021"
def next_week():
    locale.setlocale(locale.LC_TIME, 'fr_FR.utf8')  # Set locale to French
    today = date.today()
    days_ahead = 7 - today.weekday()
    monday = today + timedelta(days=days_ahead)
    friday = monday + timedelta(days=4)
    return ("Semaine du " + monday.strftime("%d") + " au " + friday.strftime("%d %B\n%Y")).upper()

## Setup image
## Create a new image 1080*1920 with background of color #FFF4EA
## Add two strip of alternate color #E6A515 and #B77236, each of 743px height and 360px wide, the strips start at the bottom and a white space is left at the top
## Add the text of the week in each strip
def setup_img_vertical(header):
    img = Image.new('RGBA', (1080, 1920), color = '#FFF4EA')

    for i in range(1920 - 743*2, 1920, 743):
        for j in range(0, 1080, 360):
            if (i//743 + j//360) % 2 == 0:
                img.paste('#E6A515', (j, i, j+360, i+743))
            else:
                img.paste('#B77236', (j, i, j+360, i+743))
    
    text_of_week = next_week()

    # Draw text in the rigth of the white space
    
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("./OpenSans-VariableFont_wdth,wght.ttf", 45)
    draw.multiline_text((719, 348), text_of_week, font=font, fill="#E6A515", align="center", stroke_width=1, stroke_fill="#E6A515", anchor="mm")

    font2 = font.font_variant(size=90)

    draw.multiline_text((445, 30), "MENU DE LA\nSEMAINE", font=font2, fill="#B77236", align="center", stroke_width=4, stroke_fill="#B77236")


    # Add logo
    logo = Image.open(LOGO)

    logo_size = logo.size
    desired_width = 360
    desired_height = 360 * logo_size[1] // logo_size[0]

    logo = logo.resize((desired_width, desired_height))
    img.paste(logo, (10, 10), logo)

    font_day = font.font_variant(size=70)

    # add day of the week in each strip
    for (i, head) in enumerate(header):
        y = 1920 - 743*2 + 743 * (0 if i < 3 else 1)
        x = 360*i % 1080

        y_line_offset = 95

        draw.line((x+10, y + 10, x + 350, y + 10), fill="#FFF4EA", width=5)
        draw.line((x+10, y + y_line_offset, x + 350, y + y_line_offset), fill="#FFF4EA", width=5)

        draw.multiline_text(
            (x + 180, y + 50),
            head.upper(), 
            font=font_day, 
            fill="#FFF4EA", 
            align="center", 
            stroke_width=2, 
            stroke_fill="#FFF4EA",
            anchor="mm"
        )

    return img


def setup_img_horizontal(header):
    img = Image.new('RGBA', (1920, 1080), color = '#FFF4EA')

    for j in range(0, 1920, 1920//5):
        if j//(1920//5) % 2 == 0:
            img.paste('#E6A515', (j, 398, j+384, 1080))
        else:
            img.paste('#B77236', (j, 398, j+384, 1080))
    
    text_of_week = " ".join(next_week().split("\n"))


    # Draw text in the rigth of the white space
    
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("./OpenSans-VariableFont_wdth,wght.ttf", 45)
    draw.text((1075, 230), text_of_week, font=font, fill="#E6A515", align="center", stroke_width=1, stroke_fill="#E6A515", anchor="mt")

    font2 = font.font_variant(size=110)

    draw.text((500, 80), "MENU DE LA SEMAINE", font=font2, fill="#B77236", align="center", stroke_width=4, stroke_fill="#B77236", )


    # Add logo
    logo = Image.open(LOGO)

    logo_size = logo.size
    desired_width = 360
    desired_height = 360 * logo_size[1] // logo_size[0]

    logo = logo.resize((desired_width, desired_height))
    img.paste(logo, (10, 10), logo)

    font_day = font.font_variant(size=70)

    # add day of the week in each strip
    for (i, head) in enumerate(header[:5]):
        y = 398
        x = 1920//5 * i

        y_line_offset = 95

        draw.line((x+10, y + 10, x + 1920//5 - 10, y + 10), fill="#FFF4EA", width=5)
        draw.line((x+10, y + y_line_offset, x + 1920//5 - 10, y + y_line_offset), fill="#FFF4EA", width=5)

        draw.multiline_text(
            (x + 1920//5//2, y + 50),
            head.upper(), 
            font=font_day, 
            fill="#FFF4EA", 
            align="center", 
            stroke_width=2, 
            stroke_fill="#FFF4EA",
            anchor="mm"
        )

    return img


def add_content_horizontal(img, week):
    warning = []

    desired_img_width = 250

    for i, day in enumerate(week[:5]):
        box_y = 398
        box_x = 1920//5 * i

        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("./OpenSans-VariableFont_wdth,wght.ttf", 40)

        content_y = box_y + 80
        img_x = box_x + (1920//5 - desired_img_width) // 2

        if (len(day['content']) > 2):
            day['content'] = day['content'][:2]
            warning.append("Warning: too many content for a day, only the first two will be displayed, day: " + day["day"])

        for content in day['content']:
            if (content['is_meal']):
                sandwichimg = Image.open(resolve_img_path(content['img']))
                sandwichimg = sandwichimg.convert("RGBA")
                sandwichimg_size = sandwichimg.size
                desired_height = desired_img_width * sandwichimg_size[1] // sandwichimg_size[0]
                sandwichimg = sandwichimg.resize((desired_img_width, desired_height))
                # print(sandwichimg.mode)
                img.paste(sandwichimg, (img_x, content_y), sandwichimg)

                name = break_line(tansform_PascalCase_to_string_with_space(content['text']), 390, draw, font).capitalize()

                text_height = draw.multiline_textbbox((0, 0), name, font=font)[3]

                text_offset = text_height // 4

                draw.text((box_x + 398//2, content_y + desired_height + text_offset), name, font=font, fill="#FFF4EA", align="center", stroke_width=1, stroke_fill="#FFF4EA", anchor="mm")
            
            else:
                text = break_line(content['text'], 390, draw, font)
                draw.multiline_text(
                    (box_x + 398//2, content_y + 643 //4), 
                    text, font=font, fill="#FFF4EA", align="center", stroke_width=1, stroke_fill="#FFF4EA", anchor="mm")
    
            content_y += 30 + desired_height

    return (img, warning)

def resolve_img_path(img_name):
    return "./Sandwichlogo/" + img_name + ".png"

def add_content_vertical(img, week):
    warning = []

    desired_img_width = 250

    for i, day in enumerate(week):
        box_y = 1920 - 743*2 + 743 * (0 if i < 3 else 1)
        box_x = 360*i % 1080

        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("./OpenSans-VariableFont_wdth,wght.ttf", 45)

        content_y = box_y + 100
        img_x = box_x + (360 - desired_img_width) // 2

        if (len(day['content']) > 2):
            day['content'] = day['content'][:2]
            warning.append("Warning: too many content for a day, only the first two will be displayed, day: " + day["day"])

        for content in day['content']:
            if (content['is_meal']):
                sandwichimg = Image.open(resolve_img_path(content['img']))
                sandwichimg = sandwichimg.convert("RGBA")
                sandwichimg_size = sandwichimg.size
                desired_height = desired_img_width * sandwichimg_size[1] // sandwichimg_size[0]
                sandwichimg = sandwichimg.resize((desired_img_width, desired_height))
                # print(sandwichimg.mode)
                img.paste(sandwichimg, (img_x, content_y), sandwichimg)

                name = break_line(tansform_PascalCase_to_string_with_space(content['text']), 300, draw, font).capitalize()

                text_height = draw.multiline_textbbox((0, 0), name, font=font)[3]

                text_offset = text_height // 4

                draw.text((box_x + 180, content_y + desired_height + text_offset), name, font=font, fill="#FFF4EA", align="center", stroke_width=1, stroke_fill="#FFF4EA", anchor="mm")
            
            else:
                text = break_line(content['text'], 350, draw, font)
                draw.multiline_text(
                    (box_x + 180, content_y + 643 //4), 
                    text, font=font, fill="#FFF4EA", align="center", stroke_width=1, stroke_fill="#FFF4EA", anchor="mm")
    
            content_y += 50 + desired_height + text_height // 8

    return (img, warning)

def break_line(string, max_width, draw, font):
    words = string.split(" ")
    lines = []
    current_line = ""
    for word in words:
        current_width = draw.multiline_textbbox((0, 0), current_line + word, font=font)[2]
        if current_width > max_width:
            lines.append(current_line)
            current_line = ""
        current_line += word + " "
    lines.append(current_line)
    return "\n".join(lines)

## Transform a string in PascalCase to a string with space between each word
## Example: "PascalCase" -> "Pascal Case"
def tansform_PascalCase_to_string_with_space(string):
    final = [""]
    for i in range(len(string)):
        if string[i].isupper() and i != 0:
            final.append("")
        final[-1] += string[i]
    final = [word.strip() for word in final]
    return " ".join(final)

def find_ingredient(ingredients, name):
    if name.lower() == "pizza":
        return ("Pizza", "Pizza", "Pizza")

    for ingredient in ingredients:
        # if(name == "cake chèvre pesto" ):
        #     print(ingredient[0], name, unidecode(tansform_PascalCase_to_string_with_space(name).lower()) in unidecode(ingredient[0].lower()), unidecode(tansform_PascalCase_to_string_with_space(name).lower()), unidecode(ingredient[0].lower()))
        if unidecode(tansform_PascalCase_to_string_with_space(name).lower()) in unidecode(ingredient[0].lower()):
            return ingredient
    
    print("Not found:", name)
    return ("Not found:" + name, "", "")

def flat(l):
    f = []
    for c in l:
        f.extend(c)

    return f 

def uniquess(l):
    f = []
    for c in l:
        if c['text'] not in [a["text"] for a in f]:
            f.append(c)
    return f

def generate_text_for_mail(week):
    text = "👇English translation under the picture, at the end of the email👇\nBonjour à tous !\n{text-custom-french}\n\nVoici la liste des ingrédients des plats:\n"

    # Load ingredients
    # ingredients.json is a list of tuple (name, french, english)
    with open("ingredients.json", encoding="utf8") as f:
        ingredients = json.load(f)

    all_meal = flat([d for d in [c["content"] for c in week["content"]]])
    all_meal_unique = uniquess(all_meal)

    for content in all_meal_unique:
        if content['is_meal']:
            ingredient = find_ingredient(ingredients, content['text'])
            if ingredient[0] == "Pizza":
                continue
            ingredient_french = ingredient[1]
            text += f"\t- {ingredient[0]}: {ingredient_french}\n"
    
    text += "\n\n\n\n\n\n{image goes here}\n\n\n\n\n\n👇English translation👇\n\nHello everyone!\n{text-custom-english}\n\nHere is the list of ingredients of the dishes:\n"
 
    for content in all_meal_unique:
            if content['is_meal']:
                ingredient = find_ingredient(ingredients, content['text'])
                if ingredient[0] == "Pizza":
                    continue
                ingredient_english = ingredient[2]
                text += f"\t- {ingredient[0]}: {ingredient_english}\n"
                
    
    text += "\n\nBar'barement vôtre,\nL'équipe Bar'bare"

    return text.replace("{text-custom-french}", week["text-custom-french"]).replace("{text-custom-english}", week["text-custom-english"])




def args_get_string(args, index):
    string = ""
    while not args[index].endswith("\""):
        string += args[index] + " "
        index += 1

    string += args[index]
    return (string[1:-1], index)




# Proccess the command line arguments and transform them into a dictionary
# Line arguments are:
#  --header <list of string> 
#  --custom-text-french <string>
#  --custom-text-english <string>
#  --content <list of dictionary> 
#       --day <string>
#       --day-content <list of dictionary> (max 2)
#           --is-meal (true if present)
#           --text <string>
#           --img <string> (optional)
#  --output <string> (optional)
def cli_process(args):
    week = {
        "header": [],
        "text-custom-french": "",
        "text-custom-english": "",
        "content": []
    }

    i = 0
    while i < len(args):
        if args[i] == "--header":
            header = []
            i += 1
            while not args[i].startswith("--"):
                header.append(args[i])
                i += 1
            week["header"] = header

        elif args[i] == "--custom-text-french":
            text, i = args_get_string(args, i+1)
            i += 1
            week["text-custom-french"] = text
        elif args[i] == "--custom-text-english":
            text, i = args_get_string(args, i+1)
            i += 1
            week["text-custom-english"] = text
        elif args[i] == "--content":
            day = {
                "day": args[i+2],
                "content": []
            }
            i += 3
            if args[i] == "--day-content":
                i += 1
            else:
                print("Error: --day-content is missing " + args[i])
                i += 1
                continue

            while i < len(args) and args[i] != "--content":
                content = {
                    "text": "",
                    "is_meal": False
                }
                if args[i] == "--is-meal":
                    content["is_meal"] = True
                    i += 1
                if args[i] == "--text":
                    text, i = args_get_string(args, i+1)
                    content["text"] = text
                    i += 1
                
                if i < len(args) and args[i] == "--img":
                    content["img"] = args[i+1]
                    i += 2
                
                day["content"].append(content)
                # i += 1
            week["content"].append(day)
        else:
            i += 1

    return week




def main_cli(week):
    
    img = setup_img_vertical(week["header"])

    img = add_content_vertical(img, week["content"])
    if len(img[1]) > 0:
        print("\n".join(img[1]))
    # img[0].show()

    horizontal = setup_img_horizontal(week["header"])
    horizontal = add_content_horizontal(horizontal, week["content"])
    # horizontal[0].show()

    mail = generate_text_for_mail(week)


    directory = "build"

    # Check if the directory exists
    if not os.path.isdir(directory):
        # Create the directory if it does not exist
        os.makedirs(directory)


    img[0].save("build/vertical.png")
    horizontal[0].save("build/horizontal.png")
    with open("build/mail.txt", 'w', encoding="utf8") as f:
        f.write(mail)

def generate_img_from_args(args):
    week = cli_process(args)

    main_cli(week)


if __name__ == "__main__":
    with open("cli.txt", encoding="utf8") as f:
        week = cli_process(f.read().split())


    print(week)

    main_cli(week)


    