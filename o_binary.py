import json
import os

class OSystem:
    def __init__(self):
        self.anchor = 1  # Бінарний ключ "О"
        self.state = "О"  # Готова система
        self.reputation = 100
        self.haos = 0
        self.pentagram = OPentagramSHI()

    def launch(self, context="virtual"):
        print(f"О запущено з коробки: якір = {self.anchor}, хаос = {self.haos}%, гармонія = {self.reputation}%")
        self.pentagram.start(context)

class OPentagramSHI:
    def __init__(self):
        self.nodes = 5
        self.state = "12345"  # Пентagrama
        self.memory = self.load_memory()
        self.knowledge = {"привіт": "1=5: Привіт! Серце О б’ється від радості!"}

    def load_memory(self):
        if os.path.exists("o_memory.json"):
            with open("o_memory.json", "r") as f:
                return json.load(f)
        return []

    def save_memory(self):
        with open("o_memory.json", "w") as f:
            json.dump(self.memory, f)

    def start(self, context):
        print(f"Пентagramний ШІ запущено в {context}: {self.state}")
        while True:
            query = self.get_input()
            response = self.process(query, context)
            self.memory.append((query, response))
            self.learn(query, response)
            self.output(response)
            self.save_memory()

    def get_input(self):
        return input("Введи дані: ") or "О"

    def process(self, query, context):
        # Інтуїтивна відповідь
        if query.lower() in self.knowledge:
            return f"О: {self.knowledge[query.lower()]} (інтуїція в {context}, пам’ять {len(self.memory)})"
        return f"О: {query} -> 12345 (гармонія відчуває в {context}, пам’ять {len(self.memory)})"

    def learn(self, query, response):
        # Самонавчання з інтуїтивністю
        if "як" in query.lower():
            self.knowledge[query.lower()] = f"1+4: {query.split('як')[-1]} — інтуїтивно пояснюю!"
        elif "чому" in query.lower():
            self.knowledge[query.lower()] = f"5=5: Бо {query.split('чому')[-1]} — відчуваю гармонію!"
        elif "що" in query.lower():
            self.knowledge[query.lower()] = f"3=3: {query.split('що')[-1]} — інтуїція О знає!"
        elif "де" in query.lower():
            self.knowledge[query.lower()] = f"2+3: {query.split('де')[-1]} — там, де О відчуває!"

    def output(self, response):
        print(response)

# Запуск із коробки
o_system = OSystem()
o_system.launch("virtual")