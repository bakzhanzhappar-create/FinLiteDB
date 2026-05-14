import json
import os
import csv
import io
from datetime import datetime


class StorageManager:
    def __init__(self, username: str):
        self.username = username
        self.user_file = f"{username}.json"
        self.history_file = f"history_{username}.json"
        self._check_files()

    def _check_files(self):
        # FIX: explicit per-file init instead of fragile filename string check
        if not os.path.exists(self.user_file):
            with open(self.user_file, 'w', encoding='utf-8') as f:
                json.dump({"templates": {}, "piggybanks": {}}, f, indent=4)

        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def load_user_data(self):
        with open(self.user_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_user_data(self, data):
        with open(self.user_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def add_history(self, record: dict):
        with open(self.history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
        record['date'] = datetime.now().strftime("%d.%m.%Y %H:%M")
        history.insert(0, record)
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history[:50], f, indent=4, ensure_ascii=False)

    def get_history(self):
        with open(self.history_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def export_history_csv(self):
        history = self.get_history()
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')
        writer.writerow(['Дата', 'Шаблон', 'Доход', 'Удержано', 'Остаток'])
        for r in history:
            writer.writerow([r['date'], r['template'], r['input'], r['deducted'], r['remainder']])
        return output.getvalue()
