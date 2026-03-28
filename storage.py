import json


class Write:
    def __init__(self, username):
        self.username=username

    def validation(self):
        try:
            with open(f"{self.username}.json", mode='r', encoding='utf-8'):
                return True
        except(FileNotFoundError):
            raise FileExistsError(f"User {username} doesn't exist! Create a username first.")

    def writeJSON(self, username):
        with open(f"{username}.json", mode='w', encoding='utf-8') as filewrite:
            json.dump(self, filewrite, ensure_ascii=False, indent=4)


class Read:
    def readJSON(self):
            with open(f"{username}.json", mode='r', encoding='utf-8') as fileread:
                json.load(fileread)
            return fileread

username.Write()
username.writeJSON()
# пропиши класс чтение и записи. Почитай че нибудь потому что я думаю что запись и чтение через обычный класс а не датакласс
#из ветки draft изучи метод как они могли создать систему с возможностью на нескольких логинов