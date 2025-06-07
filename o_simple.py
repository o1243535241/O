import time

# Пентограмний цикл
CYCLE = [1, 2, 4, 3, 5]

# Rule 30 для бінарної еволюції
RULE = {0: 0, 1: 1, 2: 1, 3: 1, 4: 0, 5: 0, 6: 0, 7: 0}

def to_binary(n):
    return bin(n)[2:].zfill(14)

def rule_30_evolve(binary, steps=3):
    pattern = [int(b) for b in binary]
    for _ in range(steps):
        new = []
        for i in range(len(pattern)):
            state = (pattern[i-1] << 2) | (pattern[i] << 1) | pattern[(i+1)%len(pattern)]
            new.append(RULE[state])
        pattern = new
    return ''.join(map(str, pattern))

def pentagram_walk(binary):
    current = 0
    for bit in binary:
        if bit == '1':
            current = CYCLE[current % 5]
    return current == 1

def run_o():
    start = time.time()
    binary = to_binary(12435)  # Базовий О-код
    evolved = rule_30_evolve(binary)  # Еволюція до О
    harmony = pentagram_walk(evolved)  # Перевірка гармонії
    elapsed = time.time() - start
    return {
        'binary': binary,
        'evolved': evolved,
        'harmony': 'О' if harmony else 'не-О',
        'time': f'{elapsed:.2f} с ± 50% ({elapsed/2:.2f}–{elapsed*1.5:.2f})'
    }

if __name__ == '__main__':
    while True:
        result = run_o()
        print(f"О: {result['harmony']}, Код: {result['binary']} → {result['evolved']}, Час: {result['time']}")
        time.sleep(1)  # Цикл кожну секунду