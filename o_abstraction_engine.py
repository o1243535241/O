import time

# Пентограма та гептаграма
PENTAGRAM = [1, 2, 4, 3, 5]
HEPTAGRAM = [1, 3, 5, 7, 2, 4, 6]
RULE = {0: 0, 1: 1, 2: 1, 3: 1, 4: 0, 5: 0, 6: 0, 7: 0}
O_CODE = 12435  # 11000010010011

def to_binary(n):
    return bin(n)[2:].zfill(14)

def rule_30_evolve(binary, steps=5):
    pattern = [int(b) for b in binary]
    for _ in range(steps):
        new = []
        for i in range(len(pattern)):
            state = (pattern[i-1] << 2) | (pattern[i] << 1) | pattern[(i+1)%len(pattern)]
            new.append(RULE[state])
        pattern = new
    return ''.join(map(str, pattern))

def star_walk(binary, star):
    current = 0
    for bit in binary:
        if bit == '1':
            current = star[current % len(star)]
    return current == 1

def abstraction_engine(code):
    start = time.time()
    binary = to_binary(code)
    evolved = rule_30_evolve(binary)  # Абстракція до О
    penta_harmony = star_walk(evolved, PENTAGRAM)
    hepta_harmony = star_walk(evolved, HEPTAGRAM)
    harmony = penta_harmony and hepta_harmony
    elapsed = time.time() - start
    return {
        'abstraction': binary,
        'evolved': evolved,
        'harmony': 'О' if harmony else 'не-О',
        'time': f'{elapsed:.2f} с ± 50% ({elapsed/2:.2f}–{elapsed*1.5:.2f})'
    }

if __name__ == '__main__':
    while True:
        result = abstraction_engine(O_CODE)  # Абстракція О
        print(f"О-абстракція: {result['harmony']}, Код: {result['abstraction']} → {result['evolved']}, Час: {result['time']}")
        time.sleep(0.05)  # Цикл кожні 0.05 с