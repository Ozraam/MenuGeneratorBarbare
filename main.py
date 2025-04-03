import json
import os
from datetime import date, timedelta
import locale
from unidecode import unidecode
from PIL import Image, ImageDraw, ImageFont

# Constants
LOGO_PATH = "Barbare.png"
FONT_PATH = "./OpenSans-VariableFont_wdth,wght.ttf"
COLORS = {
    "background": "#FFF4EA",
    "primary": "#E6A515",
    "secondary": "#B77236",
    "text": "#FFF4EA"
}
SANDWICH_DIR = "./Sandwichlogo/"
OUTPUT_DIR = "build"

class MenuGenerator:
    def __init__(self):
        self.ensure_output_directory()
        locale.setlocale(locale.LC_TIME, 'fr_FR.utf8')  # Set locale to French
        
        # Define layout configurations for vertical and horizontal formats
        self.layouts = {
            "vertical": {
                "image_size": (1080, 1920),
                "title_position": (445, 30),
                "title_text": "MENU DE LA\nSEMAINE",
                "title_font_size": 90,
                "week_text_position": (719, 348),
                "week_text_anchor": "mm",
                "week_font_size": 45,
                "grid": {
                    "rows": 2,
                    "cols": 3,
                    "cell_width": 360,
                    "cell_height": 743,
                    "y_start": 1920 - 743*2
                },
                "day_font_size": 70,
                "content_font_size": 45,
                "max_text_width": 300,
                "content_spacing": 50
            },
            "horizontal": {
                "image_size": (1920, 1080),
                "title_position": (500, 80),
                "title_text": "MENU DE LA SEMAINE",
                "title_font_size": 110,
                "week_text_position": (1075, 230),
                "week_text_anchor": "mt",
                "week_font_size": 45,
                "grid": {
                    "rows": 1,
                    "cols": 5,
                    "cell_width": 1920 // 5,
                    "cell_height": 682,
                    "y_start": 398
                },
                "day_font_size": 70,
                "content_font_size": 40,
                "max_text_width": 390,
                "content_spacing": 30
            }
        }
        
    def ensure_output_directory(self):
        """Ensure the output directory exists"""
        if not os.path.isdir(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
            
    def get_next_week_text(self):
        """Return the date of the next Monday and Friday in French format"""
        today = date.today()
        days_ahead = 7 - today.weekday()
        monday = today + timedelta(days=days_ahead)
        friday = monday + timedelta(days=4)
        return ("Semaine du " + monday.strftime("%d") + " au " + friday.strftime("%d %B\n%Y")).upper()
    
    def get_font(self, size):
        """Get a font with the specified size"""
        return ImageFont.truetype(FONT_PATH, size)
    
    def create_base_image(self, layout_type):
        """Create a new image with the specified layout"""
        layout = self.layouts[layout_type]
        return Image.new('RGBA', layout["image_size"], color=COLORS["background"])
    
    def draw_header(self, img, layout_type):
        """Draw the header with logo and title text"""
        layout = self.layouts[layout_type]
        draw = ImageDraw.Draw(img)
        
        # Add logo
        logo = Image.open(LOGO_PATH)
        logo_size = logo.size
        desired_width = 360
        desired_height = int(360 * logo_size[1] / logo_size[0])
        logo = logo.resize((desired_width, desired_height))
        img.paste(logo, (10, 10), logo)
        
        # Draw title
        title_font = self.get_font(layout["title_font_size"])
        draw.multiline_text(
            layout["title_position"], 
            layout["title_text"], 
            font=title_font, 
            fill=COLORS["secondary"], 
            align="center", 
            stroke_width=4, 
            stroke_fill=COLORS["secondary"]
        )
        
        # Draw week text
        week_text = self.get_next_week_text()
        if layout_type == "horizontal":
            week_text = " ".join(week_text.split("\n"))
            
        week_font = self.get_font(layout["week_font_size"])
        draw.text(
            layout["week_text_position"], 
            week_text, 
            font=week_font, 
            fill=COLORS["primary"], 
            align="center", 
            stroke_width=1, 
            stroke_fill=COLORS["primary"], 
            anchor=layout["week_text_anchor"]
        )
            
        return img
    
    def create_day_grid(self, img, header, layout_type):
        """Create the grid of days with alternating colors"""
        layout = self.layouts[layout_type]
        grid = layout["grid"]
        draw = ImageDraw.Draw(img)
        
        # Create grid with alternating colors
        for row in range(grid["rows"]):
            for col in range(grid["cols"]):
                y = grid["y_start"] + (row * grid["cell_height"])
                x = col * grid["cell_width"]
                
                # Choose color based on alternating pattern
                color = COLORS["primary"] if (row + col) % 2 == 0 else COLORS["secondary"]
                
                # Fill cell with color
                img.paste(color, (
                    x, 
                    y, 
                    x + grid["cell_width"], 
                    y + grid["cell_height"]
                ))
        
        # Add day headers to each cell
        font_day = self.get_font(layout["day_font_size"])
        days_to_process = header[:grid["rows"] * grid["cols"]]
        
        for i, day in enumerate(days_to_process):
            if i >= grid["rows"] * grid["cols"]:
                break
                
            row = i // grid["cols"]
            col = i % grid["cols"]
            
            y = grid["y_start"] + (row * grid["cell_height"])
            x = col * grid["cell_width"]
            
            # Draw separator lines
            y_line_offset = 95
            line_start_x = x + 10
            line_end_x = x + grid["cell_width"] - 10
            
            draw.line(
                (line_start_x, y + 10, line_end_x, y + 10), 
                fill=COLORS["background"], 
                width=5
            )
            draw.line(
                (line_start_x, y + y_line_offset, line_end_x, y + y_line_offset), 
                fill=COLORS["background"], 
                width=5
            )
            
            # Draw day text
            draw.multiline_text(
                (x + grid["cell_width"]//2, y + 50),
                day.upper(), 
                font=font_day, 
                fill=COLORS["text"], 
                align="center", 
                stroke_width=2, 
                stroke_fill=COLORS["text"],
                anchor="mm"
            )
                
        return img
    
    def break_line(self, string, max_width, draw, font):
        """Break text into multiple lines to fit within max_width"""
        if string == "RSAv":
            return string
            
        words = string.split(" ")
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            current_width = draw.multiline_textbbox((0, 0), test_line, font=font)[2]
            
            if current_width > max_width:
                lines.append(current_line)
                current_line = word + " "
            else:
                current_line = test_line
                
        lines.append(current_line)
        return "\n".join(lines)
    
    def add_content(self, img, week_data, layout_type):
        """Add content to the image based on layout"""
        layout = self.layouts[layout_type]
        grid = layout["grid"]
        warnings = []
        desired_img_width = 250
        draw = ImageDraw.Draw(img)
        
        # Get the number of cells based on the layout
        max_cells = grid["rows"] * grid["cols"]
        days_to_process = week_data[:max_cells]
        font = self.get_font(layout["content_font_size"])
            
        for i, day in enumerate(days_to_process):
            if i >= max_cells:
                break
                
            # Calculate cell position
            row = i // grid["cols"]
            col = i % grid["cols"]
            
            box_y = grid["y_start"] + (row * grid["cell_height"])
            box_x = col * grid["cell_width"]
            center_x = box_x + grid["cell_width"] // 2
                
            content_y = box_y + 100  # Initial y position for content
            img_x = box_x + (grid["cell_width"] - desired_img_width) // 2
            
            # Limit to 2 content items per day
            if len(day['content']) > 2:
                day['content'] = day['content'][:2]
                warnings.append(f"Warning: too many content for a day, only the first two will be displayed, day: {day['day']}")
                
            for content in day['content']:
                if content['is_meal']:
                    # Add meal image
                    sandwich_path = SANDWICH_DIR + content['img'] + ".png"
                    sandwich_img = Image.open(sandwich_path).convert("RGBA")
                    sandwich_size = sandwich_img.size
                    desired_height = int(desired_img_width * sandwich_size[1] / sandwich_size[0])
                    sandwich_img = sandwich_img.resize((desired_img_width, desired_height))
                    img.paste(sandwich_img, (img_x, content_y), sandwich_img)
                    
                    # Add meal text
                    formatted_text = self.break_line(content['text'], layout["max_text_width"], draw, font)
                    text_height = draw.multiline_textbbox((0, 0), formatted_text, font=font)[3]
                    text_offset = text_height // 4
                    
                    draw.text(
                        (center_x, content_y + desired_height + text_offset), 
                        formatted_text, 
                        font=font, 
                        fill=COLORS["text"], 
                        align="center", 
                        stroke_width=1, 
                        stroke_fill=COLORS["text"], 
                        anchor="mm"
                    )
                    
                    content_y_increment = desired_height + text_height // 8
                else:
                    # Add non-meal text
                    formatted_text = self.break_line(content['text'], layout["max_text_width"], draw, font)
                    
                    draw.multiline_text(
                        (center_x, content_y + (grid["cell_height"] // 4)), 
                        formatted_text, 
                        font=font, 
                        fill=COLORS["text"], 
                        align="center", 
                        stroke_width=1, 
                        stroke_fill=COLORS["text"], 
                        anchor="mm"
                    )
                    
                    content_y_increment = grid["cell_height"] // 3
                    
                # Increment y position for next content
                content_y += layout["content_spacing"] + content_y_increment
                
        return img, warnings
    
    def transform_pascal_case(self, string):
        """Transform PascalCase to space-separated words"""
        if string == "RSAv":
            return string
            
        final = [""]
        for i in range(len(string)):
            if string[i].isupper() and i != 0:
                final.append("")
            final[-1] += string[i]
            
        return " ".join(word.strip() for word in final)
    
    def find_ingredient(self, ingredients, name):
        """Find ingredient information in the ingredients list"""
        if name.lower() == "pizza":
            return ("Pizza", "Pizza", "Pizza")
            
        for ingredient in ingredients:
            if unidecode(name.lower()) in unidecode(ingredient[0].lower()):
                return ingredient
                
        print(f"Not found: {name}")
        return (f"Not found:{name}", "", "")
    
    def flatten_meals(self, week_data):
        """Flatten the nested meal structure and remove duplicates"""
        all_meals = []
        for day in week_data["content"]:
            for content in day["content"]:
                all_meals.append(content)
                
        # Remove duplicates based on text field
        unique_meals = []
        seen_texts = set()
        for meal in all_meals:
            if meal['text'] not in seen_texts:
                unique_meals.append(meal)
                seen_texts.add(meal['text'])
                
        return unique_meals
    
    def generate_email_text(self, week_data):
        """Generate text for email with ingredient information"""
        # Load ingredients
        with open("ingredients.json", encoding="utf8") as f:
            ingredients = json.load(f)
            
        unique_meals = self.flatten_meals(week_data)
        
        # Start building the email text
        text = "👇English translation under the picture, at the end of the email👇\nBonjour à tous !\n{text-custom-french}\n\nVoici la liste des ingrédients des plats:\n"
        
        # Add French ingredients
        for meal in unique_meals:
            if meal['is_meal']:
                ingredient = self.find_ingredient(ingredients, meal['text'])
                if ingredient[0] == "Pizza":
                    continue
                text += f"\t- {ingredient[0]}: {ingredient[1]}\n"
        
        # Add English translation
        text += "\n\n\n\n\n\n{image goes here}\n\n\n\n\n\n👇English translation👇\n\nHello everyone!\n{text-custom-english}\n\nHere is the list of ingredients of the dishes:\n"
        
        # Add English ingredients
        for meal in unique_meals:
            if meal['is_meal']:
                ingredient = self.find_ingredient(ingredients, meal['text'])
                if ingredient[0] == "Pizza":
                    continue
                text += f"\t- {ingredient[0]}: {ingredient[2]}\n"
                
        text += "\n\nBar'barement vôtre,\nL'équipe Bar'bare"
        
        # Replace placeholders with custom text
        return text.replace("{text-custom-french}", week_data["text-custom-french"]).replace("{text-custom-english}", week_data["text-custom-english"])
    
    def generate_menu(self, week_data, filename):
        """Generate all menu artifacts: vertical image, horizontal image, and email text"""
        # Create vertical image
        vertical_img = self.create_base_image("vertical")
        vertical_img = self.draw_header(vertical_img, "vertical")
        vertical_img = self.create_day_grid(vertical_img, week_data["header"], "vertical")
        vertical_img, v_warnings = self.add_content(vertical_img, week_data["content"], "vertical")
        
        # Create horizontal image
        horizontal_img = self.create_base_image("horizontal")
        horizontal_img = self.draw_header(horizontal_img, "horizontal")
        horizontal_img = self.create_day_grid(horizontal_img, week_data["header"], "horizontal")
        horizontal_img, h_warnings = self.add_content(horizontal_img, week_data["content"], "horizontal")
        
        # Generate email text
        email_text = self.generate_email_text(week_data)
        
        # Save outputs
        vertical_img.save(f"{OUTPUT_DIR}/{filename}-vertical.png")
        horizontal_img.save(f"{OUTPUT_DIR}/{filename}-horizontal.png")
        
        with open(f"{OUTPUT_DIR}/mail.txt", 'w', encoding="utf8") as f:
            f.write(email_text)
            
        # Print any warnings
        warnings = v_warnings + h_warnings
        if warnings:
            print("\n".join(warnings))
            
        return vertical_img, horizontal_img, email_text

class CLIParser:
    def __init__(self):
        pass
        
    def parse_string_argument(self, args, index):
        """Parse a quoted string argument"""
        string = ""
        while index < len(args) and not args[index].endswith("\""):
            string += args[index] + " "
            index += 1
            
        if index < len(args):
            string += args[index]
            
        return string[1:-1], index
    
    def parse_arguments(self, args):
        """Parse command line arguments into a structured format"""
        week_data = {
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
                while i < len(args) and not args[i].startswith("--"):
                    header.append(args[i])
                    i += 1
                week_data["header"] = header
                
            elif args[i] == "--custom-text-french":
                text, i = self.parse_string_argument(args, i+1)
                i += 1
                week_data["text-custom-french"] = text
                
            elif args[i] == "--custom-text-english":
                text, i = self.parse_string_argument(args, i+1)
                i += 1
                week_data["text-custom-english"] = text
                
            elif args[i] == "--content":
                day = {
                    "day": args[i+2],
                    "content": []
                }
                i += 3
                
                if args[i] == "--day-content":
                    i += 1
                else:
                    print(f"Error: --day-content is missing {args[i]}")
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
                        text, i = self.parse_string_argument(args, i+1)
                        content["text"] = text
                        i += 1
                    
                    if i < len(args) and args[i] == "--img":
                        content["img"] = args[i+1]
                        i += 2
                    
                    day["content"].append(content)
                    
                week_data["content"].append(day)
            else:
                i += 1
                
        return week_data

def generate_img_from_args(args, filename="menu"):
    """Main entry point for generating images from command line arguments"""
    parser = CLIParser()
    week_data = parser.parse_arguments(args)
    
    generator = MenuGenerator()
    return generator.generate_menu(week_data, filename)

if __name__ == "__main__":
    with open("cli.txt", encoding="utf8") as f:
        args = f.read().split()
        
    parser = CLIParser()
    week_data = parser.parse_arguments(args)
    
    print(week_data)
    
    generator = MenuGenerator()
    generator.generate_menu(week_data, "menu")