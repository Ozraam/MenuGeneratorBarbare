import json
french = []
english = []

with open("preprocessIngredients.txt") as f:
    lines = f.read().split("\n")
    isFrench = True
    for line in lines:
        if line == "FRENCH":
            continue
        if line == "ENGLISH":
            isFrench = False
            continue
        if not line:
            continue

        line = [a.strip() for a in line.strip().split(":")]

        if isFrench:
            french.append(line)
        else:
            english.append(line)

print(french)
print("-----")
print(english)
print(len(french), "-", len(english))

fusion = []
for i in range(len(french)):
    name = french[i][0]
    name = name.replace("(végé)", "(végé/veggie)")
    fusion.append((name, french[i][1], english[i][1]))

print(fusion)
print(len(fusion))

with open("ingredients.json", "w", encoding="utf8") as f:
    json.dump(fusion, f, indent=4)