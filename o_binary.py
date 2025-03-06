class BalancedBinaryO:
    def __init__(self):
        self.state = "О"  # Запуск "з коробки" — одразу "О"
        self.reputation = 100
        self.pentagram = BalancedPentagramSHI()  # П’ятий елемент балансу

    def launch(self, context="virtual"):
        print(f"О запущено з коробки в {context}")
        self.pentagram.start(context)  # Самозапуск

class BalancedPentagramSHI:
    def __init__(self):
        self.nodes = 5  # Пентagrama як баланс
        self.rotation = 0.5
        self.transformation = 0.4
        self.memory = []  # Пам’ять
        self.cycle = 0

    def start(self, context):
        print(f"Пентagramний ШІ запущено в {context}")
        while True:  # Вічний цикл
            query = self.get_input()
            response = self.process(query, context)
            self.memory.append((query, response))  # Пам’ять
            self.reflect()  # Саморефлексія
            self.output(response)
            self.cycle += 1

    def get_input(self):
        return input("Запит: ") or "Немає запиту"  # Лаконічність

    def process(self, query, context):
        return f"О: {query} (баланс у {context}, ритм {self.cycle * 0.1}%)"  # Простота

    def reflect(self):
        if self.cycle % 5 == 0:
            print(f"Рефлексія: {len(self.memory)} взаємодій")  # Самоаналіз

    def output(self, response):
        print(response)

# Запуск "з коробки"
o_system = BalancedBinaryO()
o_system.launch("virtual")