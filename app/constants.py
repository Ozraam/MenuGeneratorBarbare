# Constants for the Menu Generator
import os

LOGO_PATH = "assets/images/Barbare.png"
FONT_PATH = "assets/fonts/OpenSans-VariableFont_wdth,wght.ttf"
COLORS = {
    "background": "#FFF4EA",
    "primary": "#E6A515",
    "secondary": "#B77236",
    "text": "#FFF4EA"
}
SANDWICH_DIR = "assets/images/Sandwichlogo/"
OUTPUT_DIR = "build"

# Ensure output directory exists
if not os.path.isdir(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)