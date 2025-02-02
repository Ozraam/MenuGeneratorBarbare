from PIL import Image, ImageDraw, ImageFont
from datetime import date, timedelta
import locale


LOGO = "Barbare.png"

## Return the date of the next monday and the date of the next friday in the format "Semaine du 01 au 05 mars 2021"
def next_week():
    locale.setlocale(locale.LC_TIME, 'fra_fra')  # Set locale to French
    today = date.today()
    days_ahead = 7 - today.weekday()
    monday = today + timedelta(days=days_ahead)
    friday = monday + timedelta(days=4)
    return ("Semaine du " + monday.strftime("%d") + " au " + friday.strftime("%d %B\n%Y")).upper()

## Setup image
## Create a new image 1080*1920 with background of color #FFF4EA
## Add two strip of alternate color #E6A515 and #B77236, each of 743px height and 360px wide, the strips start at the bottom and a white space is left at the top
## Add the text of the week in each strip
def setup_img():
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
    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
    for i in range(5):
        y = 1920 - 743*2 + 743 * (0 if i < 3 else 1)
        x = 360*i % 1080

        y_line_offset = 95

        draw.line((x+10, y + 10, x + 350, y + 10), fill="#FFF4EA", width=5)
        draw.line((x+10, y + y_line_offset, x + 350, y + y_line_offset), fill="#FFF4EA", width=5)

        draw.multiline_text(
            (x + 180, y + 50),
            days[i].upper(), 
            font=font_day, 
            fill="#FFF4EA", 
            align="center", 
            stroke_width=2, 
            stroke_fill="#FFF4EA",
            anchor="mm"
        )

    return img

def main():
    img = setup_img()
    img.show()

if __name__ == "__main__":
    main()