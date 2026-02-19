
# storage
template_name_variable=list()
fix_number_list=list()
fix_description_list=list()
percent_number_list=list()
percent_description_list=list()

def hello():
    try:
        deal=str(input(" <<add>> add new template \n <<convert>> to convert into JSON storage\n <<read>> to show what is written in JSON storage \n <<exit>> to finish programme \n"))
        return deal
    except ValueError:
        print("Something went wrong")
        return None

def message_positive():
    print("\n--- Success! ---\n")

def message_negative():
    print("\nSomething went wrong\n")

def template_name():
    try:
        template_name_variable=str(input("Enter template name: "))
        return template_name_variable
    except ValueError:
        message_negative()
        return None

def fix():
    try:
        fix_number_list=int(input("Enter how much u need to write off from amount: "))
        return fix_number_list
    except ValueError:
        message_negative()
        print("Use only whole number!")
        return fix()

def fix_description():
    try:
        fix_description_list=str(input("Enter a description for the fix: "))
        return fix_description_list
    except ValueError:
        message_negative()
        return None

def percentage():
    try:
        percent_number_list=int(input("Enter how much u need to write off from amount by percentage: "))
        return percent_number_list
    except ValueError:
        message_negative()
        print("Use only whole number!")
        return percentage()

def percentage_description():
    try:
        percentage_description_list=str(input("Enter a description for the percentage: "))
        return percentage_description_list
    except ValueError:
        message_negative()
        return None

def full_list_append():
    try:
        template_name_variable.append(template_name())
        while True:
            ask = str(input("What do you wish to start input?\n(f/p)\nIf u sure for results write <<b>>: "))
            if ask=='p':
                percent_number_list.append(percentage())
                percent_description_list.append(percentage_description())
            if ask=='f':
                fix_number_list.append(fix())
                fix_description_list.append(fix_description())
            elif ask=='b':
                break
    except ValueError:
            message_negative()
            return None