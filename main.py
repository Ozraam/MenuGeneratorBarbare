import json
from PIL import Image, ImageDraw, ImageFont
from datetime import date, timedelta
import locale


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
    final = ""
    for i in range(len(string)):
        if string[i].isupper() and i != 0:
            final += " "
        final += string[i]
    return final

def main():

    with open("meal.json", encoding="utf8") as f:
        week = json.load(f)
    
    img = setup_img_vertical(week["header"])

    img = add_content_vertical(img, week["content"])
    if len(img[1]) > 0:
        print("\n".join(img[1]))
    #img[0].show()

    horizontal = setup_img_horizontal(week["header"])
    horizontal = add_content_horizontal(horizontal, week["content"])
    horizontal[0].show()

if __name__ == "__main__":
    main()