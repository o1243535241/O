import json  # Для збереження пам’яті у файл
import os    # Для роботи з файлами

class BalancedBinaryO:
    def __init__(self):
        self.state = "О"  # Запуск "з коробки"
        self.reputation = 100
        self.pentagram = BalancedPentagramSHI()
        self.memory_file = "o_memory.json"  # Файл для збереження пам’яті

    def launch(self, context="virtual"):
        print(f"О запущено з коробки в {context}")
        self.pentagram.start(context)

class BalancedPentagramSHI:
    def __init__(self):
        self.nodes = 5  # Пентagrama — баланс
        self.rotation = 0.5
        self.transformation = 0.4
        self.memory = self.load_memory()  # Завантажуємо пам’ять
        self.cycle = len(self.memory)  # Продовжуємо з останнього циклу
        self.knowledge = {}  # База знань для самонавчання

    def load_memory(self):
        # Завантаження пам’яті з файлу
        if os.path.exists("o_memory.json"):
            with open("o_memory.json", "r") as f:
                return json.load(f)
        return []

    def save_memory(self):
        # Збереження пам’яті у файл
        with open("o_memory.json", "w") as f:
            json.dump(self.memory, f)

    def start(self, context):
        print(f"Пентagramний ШІ запущено в {context}, пам’ять: {len(self.memory)} записів")
        while True:
            query = self.get_input()
            response = self.process(query, context)
            self.memory.append((query, response))
            self.reflect()
            self.learn(query, response)  # Самонавчання
            self.output(response)
            self.cycle += 1
            self.save_memory()  # Зберігаємо після кожного циклу

    def get_input(self):
        return input("Запит: ") or "Автозапит"

    def process(self, query, context):
        # Інтелект із самонавчанням
        if query in self.knowledge:
            return f"О: {self.knowledge[query]} (знання, ритм {self.cycle * 0.1}%)"
        return f"О: {query} оброблено (баланс у {context}, ритм {self.cycle * 0.1}%)"

    def reflect(self):
        if self.cycle % 5 == 0:
            print(f"Рефлексія: {len(self.memory)} взаємодій, знання: {len(self.knowledge)}")

    def learn(self, query, response):
        # Самонавчання: зберігаємо часті запити
        if query.lower().startswith("привіт"):
            self.knowledge[query] = "Привіт! Як справи?"
        elif "як" in query.lower():
            self.knowledge[query] = f"О пояснює: {query.split('як')[-1]} — просто!"

    def output(self, response):
        print(response)

# Запуск
o_system = BalancedBinaryO()
o_system.launch("virtual")