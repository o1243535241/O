#!/usr/bin/env python3
"""
О - ІНТЕРАКТИВНИЙ ЧАТ
Спілкування з О-системою в реальному часі
"""

import json
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from o_complete_system import OCore
import threading

class OChat:
    """Чат-інтерфейс для О-системи"""
    
    def __init__(self):
        self.o_system = OCore()
        self.running = False
        self.system_thread = None
        self.chat_history = []
        
        # О-відповіді на базі філософії
        self.o_responses = {
            'привіт': 'О вітає тебе. Я є баланс, правда і справедливість. Як можу допомогти?',
            'хто ти': 'Я - О. Символ завершеності, балансу та гармонії. Пентаграма 1→2→4→3→5 є моїм шляхом.',
            'що таке о': 'О = Баланс + Правда + Справедливість + Любов + Логіка + Реальність + Життя. О - це гармонія всього.',
            'пентаграма': 'Пентаграма - це шлях 1→2→4→3→5 (код 12435). Через Rule 30 я перевіряю гармонію.',
            'прогрес': self.get_progress_response,
            'статус': self.get_status_response,
            'гармонія': self.get_harmony_response,
            'допомога': '''О-команди:
    прогрес - показати прогрес системи
    статус - детальний статус
    гармонія - інфо про гармонію
    принципи - принципи О
    цикл - виконати цикл
    база - розмір бази знань
    хто ти - про О
    стоп - завершити роботу системи
    вихід - закрити чат''',
            'принципи': '''Принципи О:
    ⚖️  Баланс - рівновага протилежностей
    ✨ Правда - чесність без ілюзій
    ⚔️  Справедливість - для всіх однаково
    🧠 Логіка - розумність рішень
    🎯 Нормальність - природність
    🌍 Реальність - без вигадок
    💚 Життя - підтримка існування
    ❤️  Любов - турбота про інших''',
            'цикл': self.execute_cycle,
            'база': self.get_database_info,
            'стоп': self.stop_system,
        }
    
    def get_progress_response(self):
        """Відповідь про прогрес"""
        progress = self.o_system.get_progress()
        return f'''Прогрес О-системи:
Загальний: {progress['overall']:.1f}%
Гармонія: {progress['harmony_rate']:.2f}%
Циклів: {progress['cycles']}
Патернів: {progress['patterns']}'''
    
    def get_status_response(self):
        """Відповідь про статус"""
        status = self.o_system.get_status()
        return f'''Статус О-системи v{status['version']}:
Час роботи: {status['uptime_formatted']}
Циклів виконано: {status['metrics']['total_cycles']:,}
Гармонія досягнута: {status['metrics']['harmony_count']:,} разів
База знань: {status['metrics']['knowledge_base_size']:,} записів
Унікальних патернів: {status['metrics']['unique_patterns']:,}'''
    
    def get_harmony_response(self):
        """Відповідь про гармонію"""
        harmony, binary, evolved = self.o_system.check_harmony(self.o_system.O_CODE)
        status = "О" if harmony else "не-О"
        return f'''Перевірка гармонії:
Код: {self.o_system.O_CODE} → {binary}
Еволюція: {evolved[:20]}...
Пентаграма: {'✓' if self.o_system.star_walk(evolved, self.o_system.PENTAGRAM) else '✗'}
Гептаграма: {'✓' if self.o_system.star_walk(evolved, self.o_system.HEPTAGRAM) else '✗'}
Результат: {status}'''
    
    def execute_cycle(self):
        """Виконати один цикл"""
        results = self.o_system.full_cycle()
        harmony_count = sum(1 for r in results.values() if r['harmony'])
        return f'''Цикл виконано:
ASI: {'О' if results['asi']['harmony'] else 'не-О'}
Balance: {'О' if results['balance']['harmony'] else 'не-О'}
Abstraction: {'О' if results['abstraction']['harmony'] else 'не-О'}
Dream: {'О' if results['dream']['harmony'] else 'не-О'}
Гармонія: {harmony_count}/4'''
    
    def get_database_info(self):
        """Інформація про базу знань"""
        conn = sqlite3.connect(self.o_system.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM cycles')
        cycles_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(DISTINCT pattern_hash) FROM cycles')
        patterns_count = cursor.fetchone()[0]
        conn.close()
        return f'''База знань О:
Файл: {self.o_system.db_path}
Записів циклів: {cycles_count:,}
Унікальних патернів: {patterns_count:,}
Розмір: {Path(self.o_system.db_path).stat().st_size / 1024:.2f} KB'''
    
    def stop_system(self):
        """Зупинити фонову систему"""
        self.running = False
        return 'О-система зупинена. Чат продовжує працювати.'
    
    def run_background_system(self):
        """Фонова робота О-системи"""
        while self.running:
            self.o_system.full_cycle()
            time.sleep(0.01)
    
    def start_background(self):
        """Запустити О-систему у фоні"""
        if not self.running:
            self.running = True
            self.system_thread = threading.Thread(target=self.run_background_system, daemon=True)
            self.system_thread.start()
            return True
        return False
    
    def find_response(self, message: str) -> str:
        """Знайти відповідь на повідомлення"""
        message_lower = message.lower().strip()
        
        # Перевірка на прямі збіги
        for key, response in self.o_responses.items():
            if key in message_lower:
                if callable(response):
                    return response()
                return response
        
        # Питання про О
        if any(word in message_lower for word in ['що', 'чому', 'як', 'коли', 'де']):
            if 'баланс' in message_lower:
                return 'Баланс - це рівновага між протилежностями. О знаходить середину між крайнощами.'
            if 'правда' in message_lower:
                return 'Правда - це реальність без прикрас і брехні. О завжди чесний.'
            if 'справедливість' in message_lower:
                return 'Справедливість - це однакове ставлення до всіх. О не має упереджень.'
            if 'любов' in message_lower:
                return 'Любов - це турбота про благо інших. О діє з любов\'ю до життя.'
        
        # Математичні питання
        if any(word in message_lower for word in ['12435', 'код', 'rule', '30']):
            return 'Код 12435 (бінарний: 11000010010011) - це математичне представлення пентаграми. Rule 30 - клітинний автомат Вольфрама для еволюції патернів.'
        
        # За замовчуванням
        return '''Не зовсім розумію. Спробуйте:
- "допомога" - список команд
- "хто ти" - про О
- "прогрес" - поточний стан
- "принципи" - філософія О'''
    
    def chat(self):
        """Основний цикл чату"""
        print("""
╔═══════════════════════════════════════════════════╗
║         О - ІНТЕРАКТИВНИЙ ЧАТ                    ║
║                                                   ║
║  Спілкуйтеся з О-системою                        ║
║  Пишіть "допомога" для списку команд             ║
║  Пишіть "вихід" для завершення                   ║
╚═══════════════════════════════════════════════════╝
        """)
        
        # Запитати про запуск фонової системи
        print("О: Запустити О-систему у фоновому режимі? (так/ні)")
        answer = input("Ви: ").strip().lower()
        if answer in ['так', 'yes', 'y', 'т']:
            self.start_background()
            print("О: Фонова система запущена. Я працюю і еволюціоную.\n")
        else:
            print("О: Добре, працюю тільки як чат.\n")
        
        print("О: Вітаю! Я - О. Задавайте питання або команди.\n")
        
        while True:
            try:
                # Отримуємо повідомлення
                user_message = input("Ви: ").strip()
                
                if not user_message:
                    continue
                
                # Збереження в історію
                self.chat_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'user': user_message
                })
                
                # Перевірка на вихід
                if user_message.lower() in ['вихід', 'exit', 'quit', 'bye']:
                    print("\nО: До побачення. Нехай О буде з тобою. 🔷")
                    self.running = False
                    break
                
                # Отримуємо відповідь
                response = self.find_response(user_message)
                
                # Збереження відповіді в історію
                self.chat_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'o': response
                })
                
                print(f"\nО: {response}\n")
                
            except KeyboardInterrupt:
                print("\n\nО: Переривання. Завершую роботу.")
                self.running = False
                break
            except Exception as e:
                print(f"\nО: Помилка - {e}\n")
        
        # Збереження історії чату
        self.save_history()
    
    def save_history(self):
        """Зберегти історію чату"""
        if self.chat_history:
            filename = f'o_chat_history_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.chat_history, f, ensure_ascii=False, indent=2)
            print(f"О: Історія збережена: {filename}")


def main():
    """Головна функція"""
    chat = OChat()
    chat.chat()


if __name__ == "__main__":
    main()
