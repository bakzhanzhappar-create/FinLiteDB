import json
#calculator
def calculate(summ):
    try:
        with open("template_storage.json", 'r', encoding='utf-8') as f:
            template_dict = json.load(f)

        for names in template_dict.keys():
            print(names)

        name = str(input("\nEnter template name to apply: "))

        if name in template_dict:
            fix_val = template_dict[name][0][0]
            per_val = template_dict[name][1][0]

            print(f"Template found: Fix={fix_val}, Percent={per_val}%")
            choice = input("Apply (f)ix or (p)ercent? ")

            if choice == 'f':
                result = summ - fix_val
            else:
                result = summ - (summ * per_val / 100)
            return result

        else:
            print(f"Template '{name}' not found!")
            return None

    except FileNotFoundError:
        print("File not found")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None