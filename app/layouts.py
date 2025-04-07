# Layout configurations for menu generation
# Defines the visual appearance and positioning for vertical and horizontal menu formats

LAYOUTS = {
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