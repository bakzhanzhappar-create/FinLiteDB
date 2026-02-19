from reader import json_reader
from append import json_append
from dealer import hello

# storage
template_name_variable=list()
fix_number_list=list()
fix_description_list=list()
percent_number_list=list()
percent_description_list=list()


# main
while True:
    deal=hello().lower()
    if "add" in deal:
        full_list_append()

        print(template_name_variable)
        print(fix_number_list)
        print(fix_description_list)
        print(percent_number_list)
        print(percent_description_list)
        print("\n")

#converter
    if "convert" in deal:

        while len(fix_number_list) < len(template_name_variable):
            fix_number_list.append(0)
            fix_description_list.append("no fix")
        while len(percent_number_list) < len(template_name_variable):
            percent_number_list.append(0)
            percent_description_list.append("no percent")

        fix_full_list = list(zip(fix_number_list, fix_description_list))
        percent_full_list = list(zip(percent_number_list, percent_description_list))
        full_list = list(zip(fix_full_list, percent_full_list))
        template_dict = dict(zip(template_name_variable, full_list))


        template_name_variable.clear()
        fix_number_list.clear()
        fix_description_list.clear()
        percent_number_list.clear()
        percent_description_list.clear()

#JSON append
        json_append()
#JSON read
    if "read" in deal:
        json_reader()
    if "interact" in deal:
        amount = int(input("Enter amount for the template: "))
        print(f"{calculate(amount)}")

    if "exit" in deal:
        break


# формула для процентных правил 5000-(5000*7/100)=4650, если надо отнять 7% из 5000