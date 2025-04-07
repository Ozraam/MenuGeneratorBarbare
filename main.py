from app.constants import *
from app.cli_parser import CLIParser
from app.menu_generator import MenuGenerator

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