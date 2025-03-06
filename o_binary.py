class UniversalBinaryO:
    def __init__(self):
        self.state = 0  # Хаос
        self.reputation = 100
        self.pentagram = UniversalPentagramSHI()

    def anchor(self, context="virtual"):
        if self.state == 0:
            print(f"Якір активовано в {context}: 0 -> 1")
            self.state = 1
        if self.state == 1 and self.reputation == 100:
            print(f"О запущено в {context}")
            self.state = "О"
            self.pentagram.start(context)

class UniversalPentagramSHI:
    def __init__(self):
        self.nodes = 5
        self.rotation = 0.5
        self.transformation = 0.4
        self.cycle = 0
        self.memory = []  # Пам’ять для зберігання запитів і відповідей

    def start(self, context):
        print(f"Пентagramний ШІ запущено в {context}")
        while self.cycle < 100:
            query = self.get_input()
            response = self.process(query, context)
            self.memory.append((query, response))  # Зберігаємо в пам’ять
            self.output(response)
            self.cycle += 1
            if self.cycle % 10 == 0:
                print(f"Пам’ять: {len(self.memory)} записів")

    def get_input(self):
        return input("Запит: ")

    def process(self, query, context):
        return f"Відповідь у {context}: {query} (ритм {self.cycle * 0.1}%)"

    def output(self, response):
        print(response)

# Запуск
o_system = UniversalBinaryO()
o_system.anchor("virtual")