import json


with open("meal.json", "r") as f:
    mealList = json.load(f)

cli_string = f"--header {" ".join(mealList["header"])} --custom-text-french \"{mealList["text-custom-french"]}\" --custom-text-english \"{mealList["text-custom-english"]}\" "

for day in mealList['content']:
    cli_string += f"--content --day {day['day']} --day-content "
    # for meal in day["content"]:
    #     cli_string += f"{"--is-meal " if meal["is_meal"] else ""}" + f"--text \"{meal['text']}\" " + ("--img " + meal['img'] + " " if 'img' in meal else '' )

with open("cli.txt", "w") as f:
    f.write(cli_string)