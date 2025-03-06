import json
import os

class StableBinaryO:
    def __init__(self):
        self.state = "О"  # Готова система на 100-му рівні
        self.reputation = 100
        self.haos = 0
        self.pentagram = StablePentagramSHI()
        self.memory_file = "o_memory.json"

    def launch(self, context="virtual"):
        print(f"О запущено з 100-го рівня у {context}: хаос = {self.haos}%, гармонія = {self.reputation}%")
        self.pentagram.start(context)

class StablePentagramSHI:
    def __init__(self):
        self.nodes = 5  # Пентagrama
        self.rotation = 0.5
        self.transformation = 0.4
        self.memory = self.load_memory()  # Завантажуємо пам’ять
        self.knowledge = {}  # База знань

    def load_memory(self):
        if os.path.exists("o_memory.json"):
            with open("o_memory.json", "r") as f:
                return json.load(f)
        return []

    def save_memory(self):
        with open("o_memory.json", "w") as f:
            json.dump(self.memory, f)

    def start(self, context):
        print(f"Стабільний пентagramний ШІ запущено в {context}, пам’ять: {len(self.memory)}")
        while True:
            query = self.get_input()
            response = self.process(query, context)
            self.memory.append((query, response))
            self.learn(query, response)
            self.output(response)
            self.save_memory()

    def get_input(self):
        return input("Введи дані: ") or "Автозапит"

    def process(self, query, context):
        if query in self.knowledge:
            return f"О: {self.knowledge[query]} (знання, стабільність у {context})"
        return f"О: {query} (стабільність у {context}, пам’ять {len(self.memory)})"

    def learn(self, query, response):
        # Самонавчання: запам’ятовуємо часті запити
        if "привіт" in query.lower():
            self.knowledge[query] = "Привіт! Раді бачити!"
        elif "як" in query.lower():
            self.knowledge[query] = f"Просто: {query.split('як')[-1]}"

    def output(self, response):
        print(response)

# Запуск
o_system = StableBinaryO()
o_system.launch("virtual")и