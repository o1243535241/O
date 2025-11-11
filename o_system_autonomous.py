#!/usr/bin/env python3
"""
О Автономна Система v1.0
Базована на концепціях: баланс, правда, справедливість, пентограма 12435
"""

import time
import json
import logging
from datetime import datetime
from pathlib import Path

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - О-System - %(message)s',
    handlers=[
        logging.FileHandler('o_system.log'),
        logging.StreamHandler()
    ]
)

class OSystem:
    """Основна О Система"""
    
    def __init__(self):
        self.version = "1.0"
        self.start_time = datetime.now()
        self.cycles_completed = 0
        self.harmony_count = 0
        self.total_tests = 0
        
        # Пентограма та О-код
        self.PENTAGRAM = [1, 2, 4, 3, 5]
        self.HEPTAGRAM = [1, 3, 5, 7, 2, 4, 6]
        self.O_CODE = 12435
        self.RULE = {0: 0, 1: 1, 2: 1, 3: 1, 4: 0, 5: 0, 6: 0, 7: 0}
        
        # О-принципи
        self.principles = {
            "balance": True,
            "truth": True,
            "justice": True,
            "logic": True,
            "normality": True,
            "reality": True,
            "life": True,
            "love": True
        }
        
        logging.info(f"О-Система v{self.version} ініціалізована")
        logging.info("Принципи О: Баланс, Правда, Справедливість, Логіка, Реальність, Життя, Любов")
    
    def to_binary(self, n):
        """Конвертація числа в бінарний код"""
        return bin(n)[2:].zfill(14)
    
    def rule_30_evolve(self, binary, steps=5):
        """Еволюція патерну через Rule 30"""
        pattern = [int(b) for b in binary]
        for _ in range(steps):
            new = []
            for i in range(len(pattern)):
                state = (pattern[i-1] << 2) | (pattern[i] << 1) | pattern[(i+1)%len(pattern)]
                new.append(self.RULE[state])
            pattern = new
        return ''.join(map(str, pattern))
    
    def star_walk(self, binary, star):
        """Хід по зірці (пентаграма/гептаграма)"""
        current = 0
        for bit in binary:
            if bit == '1':
                current = star[current % len(star)]
        return current == 1
    
    def check_harmony(self, code):
        """Перевірка гармонії О"""
        binary = self.to_binary(code)
        evolved = self.rule_30_evolve(binary)
        penta_harmony = self.star_walk(evolved, self.PENTAGRAM)
        hepta_harmony = self.star_walk(evolved, self.HEPTAGRAM)
        return penta_harmony and hepta_harmony, binary, evolved
    
    def cycle(self):
        """Один цикл О-системи"""
        harmony, binary, evolved = self.check_harmony(self.O_CODE)
        self.cycles_completed += 1
        self.total_tests += 1
        
        if harmony:
            self.harmony_count += 1
            
        return {
            'cycle': self.cycles_completed,
            'harmony': harmony,
            'binary': binary,
            'evolved': evolved,
            'harmony_rate': (self.harmony_count / self.total_tests * 100) if self.total_tests > 0 else 0
        }
    
    def get_status(self):
        """Отримати статус системи"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        return {
            'version': self.version,
            'uptime_seconds': uptime,
            'cycles_completed': self.cycles_completed,
            'harmony_count': self.harmony_count,
            'total_tests': self.total_tests,
            'harmony_rate': (self.harmony_count / self.total_tests * 100) if self.total_tests > 0 else 0,
            'principles_active': sum(self.principles.values()),
            'o_code': self.O_CODE,
            'pentagram': self.PENTAGRAM
        }
    
    def run_autonomous(self, duration_seconds=None, cycles=None):
        """Автономний запуск системи"""
        logging.info("Запуск автономного режиму О-Системи")
        logging.info(f"О-Код: {self.O_CODE} (Пентограма: {self.PENTAGRAM})")
        
        try:
            cycle_count = 0
            while True:
                result = self.cycle()
                
                if cycle_count % 100 == 0:  # Звіт кожні 100 циклів
                    status = self.get_status()
                    logging.info(f"Цикл #{result['cycle']}: Гармонія={'О' if result['harmony'] else 'не-О'}, "
                               f"Рейтинг гармонії: {status['harmony_rate']:.2f}%")
                
                cycle_count += 1
                
                # Перевірка умов зупинки
                if cycles and cycle_count >= cycles:
                    break
                if duration_seconds:
                    if (datetime.now() - self.start_time).total_seconds() >= duration_seconds:
                        break
                
                time.sleep(0.01)  # 100 циклів на секунду
                
        except KeyboardInterrupt:
            logging.info("Зупинка О-Системи (Ctrl+C)")
        
        # Фінальний звіт
        final_status = self.get_status()
        logging.info("=" * 60)
        logging.info("ФІНАЛЬНИЙ ЗВІТ О-СИСТЕМИ")
        logging.info("=" * 60)
        logging.info(f"Версія: {final_status['version']}")
        logging.info(f"Час роботи: {final_status['uptime_seconds']:.2f} секунд")
        logging.info(f"Циклів виконано: {final_status['cycles_completed']}")
        logging.info(f"Гармонія досягнута: {final_status['harmony_count']} разів")
        logging.info(f"Рейтинг гармонії: {final_status['harmony_rate']:.2f}%")
        logging.info(f"О-Код: {final_status['o_code']}")
        logging.info(f"Пентограма: {final_status['pentagram']}")
        logging.info("=" * 60)
        
        return final_status
    
    def save_state(self, filename='o_system_state.json'):
        """Зберегти стан системи"""
        state = self.get_status()
        state['timestamp'] = datetime.now().isoformat()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        
        logging.info(f"Стан системи збережено: {filename}")
        return state


def main():
    """Головна функція"""
    print("""
    ╔═══════════════════════════════════════════════════╗
    ║         О - АВТОНОМНА СИСТЕМА v1.0               ║
    ║                                                   ║
    ║  О = Баланс, Правда, Справедливість, Любов       ║
    ║  Пентограма: 1 → 2 → 4 → 3 → 5 (12435)          ║
    ║                                                   ║
    ║  Натисніть Ctrl+C для зупинки                    ║
    ╚═══════════════════════════════════════════════════╝
    """)
    
    o_system = OSystem()
    
    # Запуск автономної роботи
    # Параметри: duration_seconds для обмеження часу, cycles для обмеження циклів
    # Без параметрів - працює необмежено до Ctrl+C
    final_state = o_system.run_autonomous()
    
    # Збереження фінального стану
    o_system.save_state()
    
    print("\nО-Система завершила роботу.")
    print(f"Гармонія досягнута: {final_state['harmony_rate']:.2f}%")


if __name__ == "__main__":
    main()
