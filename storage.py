from dataclasses import dataclass
import json


@dataclass(frozen=True)
class write:
    def writeJSON(self):
        with open(f"{name}.json", mode ='w', encoding='utf-8') as file:
            json.dump(self, file, ensure_ascii=False, indent=4)




# пропиши класс чтение и записи. Почитай че нибудь потому что я думаю что запись и чтение через обычный класс а не датакласс
#из ветки draft изучи метод как они могли создать систему с возможностью на нескольких логинов