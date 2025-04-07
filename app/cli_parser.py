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
                if i + 2 >= len(args):
                    print("Error: Missing arguments for --content")
                    i += 1
                    continue

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