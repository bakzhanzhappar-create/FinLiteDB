import json




class write:
    def validation(self):
        with open(f"{filename}.json", mode='r', encoding='utf-8') as file:

    def writeJSON(self):
        with open(f"{filename}.json", mode='w', encoding='utf-8') as file:
            json.dump(self, file, ensure_ascii=False, indent=4)




# пропиши класс чтение и записи. Почитай че нибудь потому что я думаю что запись и чтение через обычный класс а не датакласс
#из ветки draft изучи метод как они могли создать систему с возможностью на нескольких логинов