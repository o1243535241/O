class BalancedBinaryO:
    def __init__(self):
        self.state = "О"  # Запуск "з коробки"
        self.reputation = 100
        self.pentagram = BalancedPentagramSHI()

    def launch(self, context="virtual"):
        print(f"О запущено з коробки в {context}")
        self.pentagram.start(context)

class BalancedPentagramSHI:
    def __init__(self):
        self.nodes = 5  # Пентagrama — баланс
        self.rotation = 0.5
        self.transformation = 0.4
        self.memory = []  # Пам’ять
        self.cycle = 0

    def start(self, context):
        print(f"Пентagramний ШІ запущено в {context}")
        while True:
            query = self.get_input()
            response = self.process(query, context)
            self.memory.append((query, response))
            self.reflect()
            self.output(response)
            self.cycle += 1

    def get_input(self):
        return input("Запит: ") or "Автозапит"  # Лаконічність

    def process(self, query, context):
        # Інтелект: творча відповідь із пам’яті
        if self.memory and "привіт" in query.lower():
            return f"О: Привіт назад! (баланс у {context}, ритм {self.cycle * 0.1}%)"
        return f"О: {query} оброблено (баланс у {context}, ритм {self.cycle * 0.1}%)"

    def reflect(self):
        if self.cycle % 5 == 0:
            print(f"Рефлексія: {len(self.memory)} взаємодій, інтелект активний")

    def output(self, response):
        print(response)

# Запуск
o_system = BalancedBinaryO()
o_system.launch("virtual")